from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import FieldsDeff
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Any, Tuple

import struct


class FieldEncoder(TypeEncoder):
    mapped_type = InternalTypes.ANY_CTYPE

    @staticmethod
    def encode(node: TreeNode[FieldsDeff], value: Any) -> bytes:
        return struct.pack(node.data.field_impl.get_struct_token(), value)

    @staticmethod
    def decode(node: TreeNode[FieldsDeff], data: bytes) -> Tuple[float, int]:
        (value,) = struct.unpack_from(node.data.field_impl.get_struct_token(), data)
        return value, node.data.field_impl.get_byte_size()
