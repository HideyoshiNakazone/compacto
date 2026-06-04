from compacto.encoding import (
    TypeEncoder,
)
from compacto.internal_types import HasAnnotations

from typing import TypeVar


T = TypeVar("T", bound=HasAnnotations)


def pack(obj: T) -> bytes:
    return TypeEncoder.pack(obj)


def unpack(clzz: type[T], data: bytes) -> T:
    return TypeEncoder.unpack(clzz, data)
