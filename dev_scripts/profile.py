#!/usr/bin/env python
import io
import time
import gzip
from multiprocessing import cpu_count
from pathlib import Path
from random import randint

import fsspec  # type: ignore

import bgzip


VCF_FILEPATH = "s3://1000genomes/technical/working/20100929_sanger_low_coverage_snps/AFR.union.snps.20100517.sites.vcf.gz"  # noqa
UNCOMPRESSED_LENGTH = 219079695
fs = fsspec.filesystem(
    "filecache",
    target_protocol="s3",
    target_options={"anon": True},
    cache_storage=str(Path(__file__).parent.parent / "cache"),
)


class profile:
    start: float
    name: str

    def __init__(self, name="default"):
        self.name = name

    def __enter__(self, *args, **kwargs):
        self.start = time.perf_counter()

    def __exit__(self, *args, **kwargs):
        self._print(time.perf_counter() - self.start)

    def _print(self, duration):
        print(f"{self.name} took {duration} seconds")


def profile_read():
    with fs.open(VCF_FILEPATH, "rb") as raw:
        with profile("gzip read"), gzip.GzipFile(fileobj=raw) as fh:
            data = fh.read()
        assert UNCOMPRESSED_LENGTH == len(data)

    for num_threads in range(1, 1 + cpu_count()):
        with fs.open(VCF_FILEPATH, "rb") as raw, profile(
            f"BGZipReader read (num_threads={num_threads})"
        ):
            reader = bgzip.BGZipReader(raw, num_threads=num_threads)
            data = bytearray()
            while True:
                d = reader.read(randint(1024 * 1024 * 1, 1024 * 1024 * 10))
                if not d:
                    break
                try:
                    data += d
                finally:
                    d.release()
            assert UNCOMPRESSED_LENGTH == len(data)


def profile_write():
    with fs.open(VCF_FILEPATH, "rb") as raw, gzip.GzipFile(fileobj=raw) as fh:
        inflated_data = fh.read()

    with profile("gzip write"), gzip.GzipFile(fileobj=io.BytesIO(), mode="w") as fh:
        fh.write(inflated_data)

    for num_threads in range(1, 1 + cpu_count()):
        with profile(f"bgzip write (num_threads={num_threads})"), bgzip.BGZipWriter(
            io.BytesIO(), num_threads=num_threads
        ) as writer:
            n = 987345
            writer.write(inflated_data[:n])
            writer.write(inflated_data[n:])


if __name__ == "__main__":
    profile_read()
    print()
    profile_write()
