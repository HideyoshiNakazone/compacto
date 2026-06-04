from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructTyping
from compacto.utils.constants import SIZE_UNSIGNED_LONG, UNSIGNED_LONG_TYPE_TOKEN

import struct
from typing import Tuple


class StringEncoder(TypeEncoder[str]):
    mapped_type = str

    @staticmethod
    def encode(value: str) -> bytes:
        encoded = value.encode("utf-8")
        buf = bytearray(SIZE_UNSIGNED_LONG + len(encoded))
        struct.pack_into(UNSIGNED_LONG_TYPE_TOKEN, buf, 0, len(encoded))
        buf[SIZE_UNSIGNED_LONG:] = encoded
        return bytes(buf)

    @staticmethod
    def decode(_: TreeNode[StructTyping], data: bytes) -> Tuple[str, int]:
        data = memoryview(data)
        (length,) = struct.unpack_from(UNSIGNED_LONG_TYPE_TOKEN, data)
        data = data[SIZE_UNSIGNED_LONG:]
        return data[:length].tobytes().decode("utf-8"), SIZE_UNSIGNED_LONG + length
