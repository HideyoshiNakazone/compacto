from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import OptionalDeff, StructTyping
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import Any, Buffer, Optional, Tuple, Unpack

import struct


class OptionalEncoder(TypeEncoder):
    mapped_type = InternalTypes.OPTIONAL

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping],
        value: Optional[Any],
        is_little_endian: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Buffer:
        if not isinstance(node.data, OptionalDeff):
            raise TypeError(f"Unsupported field type: {type(node.data)}")

        if len(node.children) != 1:
            raise RuntimeError(
                "Failed to determine the type of list element. "
                "Type OptionalDeff node should have exactly one child field."
            )

        child_node = node.children[0]
        child_encoder = TypeEncoder.get_implementation(child_node.data.field_type)
        if not child_encoder:
            raise RuntimeError("Failed to determine the type of list element.")

        if value is None:
            return struct.pack(
                InternalTypes.BOOL.get_struct_token(is_little_endian), False
            )

        data = bytearray()

        data.extend(
            struct.pack(InternalTypes.BOOL.get_struct_token(is_little_endian), True)
        )
        data.extend(
            child_encoder.encode(
                child_node, value, is_little_endian=is_little_endian, **options
            )
        )

        return data

    @staticmethod
    def _decode(
        node: TreeNode[StructTyping],
        data: Buffer,
        is_little_endian: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Tuple[Optional[Any], int]:
        if not isinstance(node.data, OptionalDeff):
            raise TypeError(f"Unsupported field type: {type(node.data)}")

        if len(node.children) != 1:
            raise RuntimeError(
                "Failed to determine the type of list element. "
                "Type OptionalDeff node should have exactly one child field."
            )

        child_node = node.children[0]
        child_encoder = TypeEncoder.get_implementation(child_node.data.field_type)
        if not child_encoder:
            raise RuntimeError("Failed to determine the type of list element.")

        (non_null_flag,) = struct.unpack_from(
            InternalTypes.BOOL.get_struct_token(is_little_endian), data
        )
        offset = InternalTypes.BOOL.get_byte_size(is_little_endian)

        if not non_null_flag:
            return None, offset

        value, var_offset = child_encoder.decode(
            child_node, data[offset:], is_little_endian=is_little_endian, **options
        )
        return value, offset + var_offset
