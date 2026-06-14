from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import StructTyping
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Buffer, Tuple, Unpack

import struct


class StringEncoder(TypeEncoder):
    mapped_type = InternalTypes.STRING

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping],
        value: str,
        is_little_endian: bool,
        **options: Unpack[InternalOptions],
    ) -> Buffer:
        len_buff_size = InternalTypes.UINT64.get_byte_size(
            is_little_endian
        )  # the endian order is required because in some cases it can make a uint64 be only 4bytes instead of 8bytes

        encoded = value.encode("utf-8")
        buf = bytearray(len_buff_size + len(encoded))
        struct.pack_into(
            InternalTypes.UINT64.get_struct_token(is_little_endian),
            buf,
            0,
            len(encoded),
        )
        buf[len_buff_size:] = encoded

        return buf

    @staticmethod
    def _decode(
        _: TreeNode[StructTyping],
        data: Buffer,
        is_little_endian: bool,
        **options: Unpack[InternalOptions],
    ) -> Tuple[str, int]:
        len_buff_size = InternalTypes.UINT64.get_byte_size(
            is_little_endian
        )  # the endian order is required because in some cases it can make a uint64 be only 4bytes instead of 8bytes

        data = memoryview(data)
        (length,) = struct.unpack_from(
            InternalTypes.UINT64.get_struct_token(is_little_endian), data, 0
        )
        payload_data = data[len_buff_size:]
        return payload_data[:length].tobytes().decode("utf-8"), len_buff_size + length
