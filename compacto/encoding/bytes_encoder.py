from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import StructTyping
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Buffer, Tuple, Unpack

import struct


class ByteEncoder(TypeEncoder):
    mapped_type = InternalTypes.BYTES

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping],
        value: bytes,
        is_little_endian: bool,
        **options: Unpack[InternalOptions],
    ) -> bytes:
        len_buff_size = InternalTypes.UINT64.get_byte_size(is_little_endian)

        buf = bytearray(len_buff_size + len(value))
        struct.pack_into(
            InternalTypes.UINT64.get_struct_token(is_little_endian), buf, 0, len(value)
        )
        buf[len_buff_size:] = value

        return bytes(buf)

    @staticmethod
    def _decode(
        _: TreeNode[StructTyping],
        data: Buffer,
        is_little_endian: bool,
        **options: Unpack[InternalOptions],
    ) -> Tuple[bytes, int]:
        data = memoryview(data)
        (length,) = struct.unpack_from(
            InternalTypes.UINT64.get_struct_token(is_little_endian), data
        )
        len_buff_size = InternalTypes.UINT64.get_byte_size(is_little_endian)
        data = data[len_buff_size:]
        return data[:length].tobytes(), len_buff_size + length
