from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import StructTyping
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple

import struct


class ByteEncoder(TypeEncoder):
    mapped_type = InternalTypes.BYTES

    @staticmethod
    def _encode(node: TreeNode[StructTyping], value: bytes) -> bytes:
        buf = bytearray(InternalTypes.UINT64.get_byte_size() + len(value))
        struct.pack_into(InternalTypes.UINT64.get_struct_token(), buf, 0, len(value))
        buf[InternalTypes.UINT64.get_byte_size() :] = value
        return bytes(buf)

    @staticmethod
    def _decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[bytes, int]:
        data = memoryview(data)
        (length,) = struct.unpack_from(InternalTypes.UINT64.get_struct_token(), data)
        data = data[InternalTypes.UINT64.get_byte_size() :]
        return data[:length].tobytes(), InternalTypes.UINT64.get_byte_size() + length
