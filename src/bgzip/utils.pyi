from typing import Sequence, List
from bgzip import InflateInfo

block_batch_size: int
block_data_inflated_size: int
block_metadata_size: int

def inflate_chunks(
    py_chunks: Sequence[memoryview],
    py_dst_buf: memoryview,
    num_threads: int,
    atomic: bool = False,
) -> InflateInfo: ...
def deflate_to_buffers(
    py_input_buff: Sequence, py_deflated_buffers: List[bytearray], num_threads: int
) -> List[int]: ...
