from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructTyping
from compacto.utils.constants import SIZE_UNSIGNED_LONG, UNSIGNED_LONG_TYPE_TOKEN

from typing_extensions import Tuple

import struct


class ByteEncoder(TypeEncoder[bytes]):
    mapped_type = bytes

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: bytes) -> bytes:
        buf = bytearray(SIZE_UNSIGNED_LONG + len(value))
        struct.pack_into(UNSIGNED_LONG_TYPE_TOKEN, buf, 0, len(value))
        buf[SIZE_UNSIGNED_LONG:] = value
        return bytes(buf)

    @staticmethod
    def decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[bytes, int]:
        data = memoryview(data)
        (length,) = struct.unpack_from(UNSIGNED_LONG_TYPE_TOKEN, data)
        data = data[SIZE_UNSIGNED_LONG:]
        return data[:length].tobytes(), SIZE_UNSIGNED_LONG + length
