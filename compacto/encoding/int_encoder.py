from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructDeff
from compacto.utils.constants import LONG_LONG_TYPE_TOKEN, SIZE_LONG_LONG

import struct
from typing import Tuple


class IntEncoder(TypeEncoder[int]):
    mapped_type = int

    @staticmethod
    def encode(value: int) -> bytes:
        return struct.pack(LONG_LONG_TYPE_TOKEN, value)

    @staticmethod
    def decode(_: TreeNode[StructDeff], data: bytes) -> Tuple[int, int]:
        (value,) = struct.unpack_from(LONG_LONG_TYPE_TOKEN, data)
        return value, SIZE_LONG_LONG
