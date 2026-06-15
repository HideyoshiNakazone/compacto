from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import FieldsDeff, HashmapDeff
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import Any, Buffer, Tuple, Unpack

import struct


class HashmapEncoder(TypeEncoder):
    mapped_type = InternalTypes.HASHMAP

    @staticmethod
    def _encode(
        node: TreeNode[FieldsDeff],
        value: Any,
        is_little_endian: bool = False,
        is_length_64_bytes: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Buffer:
        if not isinstance(node.data, HashmapDeff):
            raise TypeError(f"Unsupported field type: {type(node.data)}")

        if len(node.children) != 2:
            raise TypeError(
                f"Expected exactly 2 child fields for HashmapDeff, got {len(node.children)}"
            )

        len_type = InternalTypes.UINT64 if is_length_64_bytes else InternalTypes.UINT32
        len_buff_size = len_type.get_byte_size(is_little_endian)

        buff = bytearray(len_buff_size)
        struct.pack_into(
            len_type.get_struct_token(is_little_endian), buff, 0, len(value)
        )

        key_node = next(
            child for child in node.children if child.data.field_name == "_key"
        )
        value_node = next(
            child for child in node.children if child.data.field_name == "_value"
        )

        for key, value in value.items():
            buff.extend(
                TypeEncoder.pack(
                    key_node,
                    key,
                    is_little_endian=is_little_endian,
                    is_length_64_bytes=is_length_64_bytes,
                    **options,
                )
            )
            buff.extend(
                TypeEncoder.pack(
                    value_node,
                    value,
                    is_little_endian=is_little_endian,
                    is_length_64_bytes=is_length_64_bytes,
                    **options,
                )
            )

        return buff

    @staticmethod
    def _decode(
        node: TreeNode[FieldsDeff],
        data: Buffer,
        is_little_endian: bool = False,
        is_length_64_bytes: bool = False,
        **options: Unpack[InternalOptions],
    ) -> Tuple[dict, int]:
        if not isinstance(node.data, HashmapDeff):
            raise TypeError(f"Unsupported field type: {type(node.data)}")

        if len(node.children) != 2:
            raise TypeError(
                f"Expected exactly 2 child fields for HashmapDeff, got {len(node.children)}"
            )

        len_type = InternalTypes.UINT64 if is_length_64_bytes else InternalTypes.UINT32
        offset = len_type.get_byte_size(is_little_endian)

        (length,) = struct.unpack_from(
            len_type.get_struct_token(is_little_endian), data, 0
        )

        key_node = next(
            child for child in node.children if child.data.field_name == "_key"
        )
        value_node = next(
            child for child in node.children if child.data.field_name == "_value"
        )

        values = {}
        for _ in range(length):
            key, key_offset = TypeEncoder.unpack(
                key_node,
                data[offset:],
                is_little_endian=is_little_endian,
                is_length_64_bytes=is_length_64_bytes,
                **options,
            )
            offset += key_offset

            value, value_offset = TypeEncoder.unpack(
                value_node,
                data[offset:],
                is_little_endian=is_little_endian,
                is_length_64_bytes=is_length_64_bytes,
                **options,
            )
            offset += value_offset

            values[key] = value

        return values, offset
