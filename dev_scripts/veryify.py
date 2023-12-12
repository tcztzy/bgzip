#!/usr/bin/env python
"""
Verify the results of bgzip are identicle to gzip for a block gzipped file.
"""
import sys
import gzip

import bgzip

filepath = sys.argv[1]

with open(filepath, "rb") as raw1:
    with open(filepath, "rb") as raw2, gzip.GzipFile(
        fileobj=raw1
    ) as gzip_reader, bgzip.BGZipReader(raw2, num_threads=6) as bgzip_reader:
        while True:
            a = bgzip_reader.read(1024 * 1024)
            b = gzip_reader.read(len(a))
            assert a == b
            if not (a or b):
                break
