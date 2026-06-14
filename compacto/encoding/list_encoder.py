from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import ListDeff, StructTyping
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Buffer, Tuple, Unpack

import struct


class ListEncoder(TypeEncoder):
    mapped_type = InternalTypes.LIST

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping],
        value: list,
        is_little_endian: bool = False,
        is_length_64_bytes: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Buffer:
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

        len_type = InternalTypes.UINT64 if is_length_64_bytes else InternalTypes.UINT32

        encoded_elements = bytearray()

        encoded_elements.extend(
            struct.pack(len_type.get_struct_token(is_little_endian), len(value))
        )

        for ele_value in value:
            encoded_elements.extend(
                child_encoder.encode(
                    child_node, ele_value, is_little_endian=is_little_endian, **options
                )
            )

        return encoded_elements

    @staticmethod
    def _decode(
        node: TreeNode[StructTyping],
        data: Buffer,
        is_little_endian: bool = False,
        is_length_64_bytes: bool = False,
        **options: Unpack[InternalOptions],
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

        len_type = InternalTypes.UINT64 if is_length_64_bytes else InternalTypes.UINT32

        (arr_len,) = struct.unpack_from(
            len_type.get_struct_token(is_little_endian), data
        )

        offset = len_type.get_byte_size(is_little_endian)
        arr_elements = []

        for _ in range(arr_len):
            elem_value, elem_offset = child_encoder.decode(
                child_node,
                data[offset:],
                is_little_endian=is_little_endian,
                **options,
            )
            arr_elements.append(elem_value)
            offset += elem_offset

        return arr_elements, offset
