from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import ListDeff, StructTyping
from compacto.utils.constants import SIZE_UNSIGNED_LONG, UNSIGNED_LONG_TYPE_TOKEN
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class ListEncoder(TypeEncoder[list]):
    mapped_type = list

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: list) -> bytes:
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
            encoded_elements.extend(child_encoder.encode(child_node, ele_value))

        return struct.pack(UNSIGNED_LONG_TYPE_TOKEN, len(value)) + encoded_elements

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[list, int]:
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
        (arr_len,) = struct.unpack_from(UNSIGNED_LONG_TYPE_TOKEN, data)

        offset = SIZE_UNSIGNED_LONG
        arr_elements = []

        for _ in range(arr_len):
            elem_value, elem_offset = child_encoder.decode(
                child_node, data[offset:].tobytes()
            )
            arr_elements.append(elem_value)
            offset += elem_offset

        return arr_elements, offset
