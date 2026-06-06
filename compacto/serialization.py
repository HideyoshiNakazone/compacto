from compacto.encoding import (
    TypeEncoder,
)
from compacto.utils.annotations import HasAnnotations

from typing_extensions import TypeVar


T = TypeVar("T", bound=HasAnnotations)


def pack(obj: T) -> bytes:
    return TypeEncoder.pack(obj)


def unpack(clzz: type[T], data: bytes) -> T:
    value, _ = TypeEncoder.unpack(clzz, data)
    return value
