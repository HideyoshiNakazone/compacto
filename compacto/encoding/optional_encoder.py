from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import OptionalDeff, StructTyping
from compacto.utils.constants import BOOL_TYPE_TOKEN, SIZE_BOOL

from typing_extensions import Any, Optional, Tuple

import struct


class OptionalEncoder(TypeEncoder[Optional]):
    mapped_type = Optional

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: Optional[Any]) -> bytes:
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
            return struct.pack(BOOL_TYPE_TOKEN, False)

        data = bytearray()

        data.extend(struct.pack(BOOL_TYPE_TOKEN, True))
        data.extend(child_encoder.encode(child_node, value))

        return data

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[Optional[Any], int]:
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

        (non_null_flag,) = struct.unpack_from(BOOL_TYPE_TOKEN, data)
        offset = SIZE_BOOL

        if not non_null_flag:
            return None, offset

        value, var_offset = child_encoder.decode(child_node, data[offset:])
        return value, offset + var_offset
