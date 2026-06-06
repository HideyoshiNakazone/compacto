from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import StructTyping
from compacto.utils.constants import (
    BOOL_TYPE_TOKEN,
    SIZE_BOOL,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class BoolEncoder(TypeEncoder[bool]):
    mapped_type = bool

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: bool) -> bytes:
        return struct.pack(BOOL_TYPE_TOKEN, value)

    @staticmethod
    def decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[bool, int]:
        (value,) = struct.unpack_from(BOOL_TYPE_TOKEN, data)
        return value, SIZE_BOOL
