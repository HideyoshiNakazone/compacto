from compacto.encoding.type_encoder import TypeEncoder
from compacto.utils.constants import (
    DOUBLE_TYPE_TOKEN,
    SIZE_DOUBLE,
)

import struct
from typing import Tuple


class FloatEncoder(TypeEncoder[float]):
    mapped_type = float

    @staticmethod
    def encode(value: float) -> bytes:
        return struct.pack(DOUBLE_TYPE_TOKEN, value)

    @staticmethod
    def decode(data: bytes) -> Tuple[float, int]:
        (value,) = struct.unpack_from(DOUBLE_TYPE_TOKEN, data)
        return value, SIZE_DOUBLE
