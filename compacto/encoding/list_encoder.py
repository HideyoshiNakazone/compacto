from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import OptionFlags
from compacto.struct_parser import ListDeff, StructTyping
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class ListEncoder(TypeEncoder):
    mapped_type = InternalTypes.LIST

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping], value: list, options: OptionFlags
    ) -> bytes:
        if not isinstance(node.data, ListDeff):
            raise TypeError(f"Unsupported field type: {type(node.data)}")

        if len(node.children) != 1:
            raise RuntimeError(
                "Failed to determine the type of list element. "
                "Type ListDeff node should have exactly one child field."
            )

        child_node = node.children[0]
        child_encoder = TypeEncoder.get_implementation(child_node.data.field_type)
        if not child_encoder:
            raise RuntimeError("Failed to determine the type of list element.")

        encoded_elements = bytearray()
        for ele_value in value:
            encoded_elements.extend(
                child_encoder.encode(child_node, ele_value, options)
            )

        return (
            struct.pack(InternalTypes.UINT64.get_struct_token(), len(value))
            + encoded_elements
        )

    @staticmethod
    def _decode(
        node: TreeNode[StructTyping], data: bytes, options: OptionFlags
    ) -> Tuple[list, int]:
        if not isinstance(node.data, ListDeff):
            raise TypeError(f"Unsupported field type: {type(node.data)}")

        if len(node.children) != 1:
            raise RuntimeError(
                "Failed to determine the type of list element. "
                "Type ListDeff node should have exactly one child field."
            )

        child_node = node.children[0]
        child_encoder = TypeEncoder.get_implementation(child_node.data.field_type)
        if not child_encoder:
            raise RuntimeError("Failed to determine the type of list element.")

        data = memoryview(data)
        (arr_len,) = struct.unpack_from(InternalTypes.UINT64.get_struct_token(), data)

        offset = InternalTypes.UINT64.get_byte_size()
        arr_elements = []

        for _ in range(arr_len):
            elem_value, elem_offset = child_encoder.decode(
                child_node, data[offset:].tobytes(), options
            )
            arr_elements.append(elem_value)
            offset += elem_offset

        return arr_elements, offset
