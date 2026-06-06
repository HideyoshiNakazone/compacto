from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import StructTyping
from compacto.utils.constants import LONG_LONG_TYPE_TOKEN, SIZE_LONG_LONG
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class IntEncoder(TypeEncoder[int]):
    mapped_type = int

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: int) -> bytes:
        return struct.pack(LONG_LONG_TYPE_TOKEN, value)

    @staticmethod
    def decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[int, int]:
        (value,) = struct.unpack_from(LONG_LONG_TYPE_TOKEN, data)
        return value, SIZE_LONG_LONG
