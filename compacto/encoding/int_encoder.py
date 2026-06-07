from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import StructTyping
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class IntEncoder(TypeEncoder[int]):
    mapped_type = int

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: int) -> bytes:
        return struct.pack(InternalTypes.INT_64.get_struct_token(), value)

    @staticmethod
    def decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[int, int]:
        (value,) = struct.unpack_from(InternalTypes.INT_64.get_struct_token(), data)
        return value, InternalTypes.INT_64.get_byte_size()
