from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import StructTyping
from compacto.utils.constants import (
    DOUBLE_TYPE_TOKEN,
    SIZE_DOUBLE,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class FloatEncoder(TypeEncoder[float]):
    mapped_type = float

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: float) -> bytes:
        return struct.pack(DOUBLE_TYPE_TOKEN, value)

    @staticmethod
    def decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[float, int]:
        (value,) = struct.unpack_from(DOUBLE_TYPE_TOKEN, data)
        return value, SIZE_DOUBLE
