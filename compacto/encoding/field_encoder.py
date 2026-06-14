from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import FieldsDeff
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Any, Buffer, Tuple, Unpack

import struct


class FieldEncoder(TypeEncoder):
    mapped_type = InternalTypes.ANY_CTYPE

    @staticmethod
    def _encode(
        node: TreeNode[FieldsDeff],
        value: Any,
        is_little_endian: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Buffer:
        return struct.pack(
            node.data.field_impl.get_struct_token(is_little_endian), value
        )

    @staticmethod
    def _decode(
        node: TreeNode[FieldsDeff],
        data: Buffer,
        is_little_endian: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Tuple[float, int]:
        (value,) = struct.unpack_from(
            node.data.field_impl.get_struct_token(is_little_endian), data
        )
        return value, node.data.field_impl.get_byte_size(is_little_endian)
