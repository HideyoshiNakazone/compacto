from compacto.internal_types import HasAnnotations, TreeNode

from typing import TypeVar

from struct_parser import StructTyping

T = TypeVar("T", bound=HasAnnotations)


def pack(obj: T) -> bytes: ...


def unpack(clzz: type[T], data: bytes) -> T: ...
