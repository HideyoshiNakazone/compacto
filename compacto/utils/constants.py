from typing_extensions import Generic, Protocol, Self, Type, TypeVar, runtime_checkable

import ctypes
from dataclasses import dataclass
from enum import Enum
from typing import Optional


@runtime_checkable
class InternalType(Protocol):
    def get_python_type(self) -> type: ...
    def get_byte_size(self) -> int | None: ...
    def get_struct_token(self) -> str | None: ...
    def is_root_type(self) -> bool: ...


@dataclass
class Ctype(InternalType):
    ctype: Type[ctypes._SimpleCData]
    root: bool = False

    def get_python_type(self) -> type:
        return type(self.ctype().value)

    def get_byte_size(self) -> int | None:
        return ctypes.sizeof(self.ctype)

    def get_struct_token(self) -> str | None:
        return self.ctype._type_

    def is_root_type(self) -> bool:
        return self.root


T = TypeVar("T", bound=type)


@dataclass
class CustomType(InternalType, Generic[T]):
    type: T

    def get_python_type(self) -> T:
        return self.type

    def get_byte_size(self) -> int | None:
        return None

    def get_struct_token(self) -> str | None:
        return None

    def is_root_type(self) -> bool:
        return True


class InternalTypes(Enum):
    BOOL = Ctype(ctypes.c_bool, root=True)

    # Integer Types
    INT_8 = Ctype(ctypes.c_int8)
    INT_16 = Ctype(ctypes.c_int16)
    INT_32 = Ctype(ctypes.c_int32)
    INT_64 = Ctype(ctypes.c_int64)
    UINT8 = Ctype(ctypes.c_uint8)
    UINT16 = Ctype(ctypes.c_uint16)
    UINT32 = Ctype(ctypes.c_uint32)
    UINT64 = Ctype(ctypes.c_uint64)
    UINT = Ctype(ctypes.c_uint)
    INT = Ctype(ctypes.c_int, root=True)

    # Floating Point Types
    FLOAT = Ctype(ctypes.c_float)
    DOUBLE = Ctype(ctypes.c_double, True)

    # Custom Types
    BYTES = CustomType(bytes)
    STRING = CustomType(str)
    LIST = CustomType(list)
    OPTIONAL = CustomType(Optional)
    OBJECT = CustomType(object)

    def get_python_type(self) -> type:
        return self.value.get_python_type()

    def get_byte_size(self) -> int | None:
        return self.value.get_byte_size()

    def get_struct_token(self) -> str | None:
        return self.value.get_struct_token()

    @classmethod
    def get_from_type(
        cls, type_: type, ctype: Optional[Type[ctypes._SimpleCData]] = None
    ) -> Self:
        for t in cls:
            if ctype is None and not t.value.is_root_type():
                continue
            if ctype is not None and t.value.ctype != ctype:
                continue

            if t.value.get_python_type() == type_:
                return t

        return cls.OBJECT
