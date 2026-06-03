from compacto.encoding.type_encoder import TypeEncoder
from compacto.utils.constants import (
    BOOL_TYPE_TOKEN,
    SIZE_BOOL,
)

import struct
from typing import Tuple


class BoolEncoder(TypeEncoder[bool]):
    mapped_type = bool

    @staticmethod
    def encode(value: bool) -> bytes:
        return struct.pack(BOOL_TYPE_TOKEN, value)

    @staticmethod
    def decode(data: bytes) -> Tuple[bool, int]:
        (value,) = struct.unpack_from(BOOL_TYPE_TOKEN, data)
        return value, SIZE_BOOL
