from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructTyping
from compacto.utils.constants import SIZE_UNSIGNED_LONG, UNSIGNED_LONG_TYPE_TOKEN

import struct
from typing import Tuple


class ListEncoder(TypeEncoder[list]):
    mapped_type = list

    @staticmethod
    def encode(value: list) -> bytes:
        arr_len = len(value)

        encoded_elements = []
        for ele_value in value:
            encoded_elements.append(TypeEncoder.pack(ele_value))

        return struct.pack(UNSIGNED_LONG_TYPE_TOKEN, arr_len) + b"".join(
            encoded_elements
        )

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[list, int]:
        if not node.children or (elem_node := node.children[0]) is None:
            raise RuntimeError("Failed to determine the type of list element.")

        element_clzz = elem_node.data.field_type
        elem_encoder = TypeEncoder.get_implementation(element_clzz)
        if not elem_encoder:
            raise RuntimeError("Failed to determine the type of list element.")

        data = memoryview(data)
        (arr_len,) = struct.unpack_from(UNSIGNED_LONG_TYPE_TOKEN, data)

        offset = SIZE_UNSIGNED_LONG
        arr_elements = []

        for _ in range(arr_len):
            elem_value, elem_offset = elem_encoder.decode(elem_node, data[offset:])
            arr_elements.append(elem_value)
            offset += elem_offset

        return arr_elements, offset
