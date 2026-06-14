from compacto.utils.constants import InternalTypes

from typing_extensions import Union

import ctypes
from dataclasses import dataclass


@dataclass
class InternalTestClass:
    field: int


class TestInternalTypes:
    def test_get_byte_size(self) -> None:
        assert InternalTypes.BOOL.value.get_byte_size(True) == 1

    def test_get_from_type_with_ctype(self) -> None:
        assert InternalTypes.get_from_type(bool, ...) == InternalTypes.BOOL

        assert InternalTypes.get_from_type(int, ...) == InternalTypes.INT
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_int8)
            == InternalTypes.INT_8
        )
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_int16)
            == InternalTypes.INT_16
        )
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_int32)
            == InternalTypes.INT_32
        )
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_int64)
            == InternalTypes.INT_64
        )

        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_uint8)
            == InternalTypes.UINT8
        )
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_uint16)
            == InternalTypes.UINT16
        )
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_uint32)
            == InternalTypes.UINT32
        )
        assert (
            InternalTypes.get_from_type(int, ..., ctype=ctypes.c_uint64)
            == InternalTypes.UINT64
        )

        assert InternalTypes.get_from_type(float, ...) == InternalTypes.DOUBLE
        assert (
            InternalTypes.get_from_type(float, ..., ctype=ctypes.c_double)
            == InternalTypes.DOUBLE
        )

    def test_get_from_type_with_custom_types(self) -> None:
        assert InternalTypes.get_from_type(bytes, ...) == InternalTypes.BYTES
        assert InternalTypes.get_from_type(str, ...) == InternalTypes.STRING
        assert InternalTypes.get_from_type(list, ...) == InternalTypes.LIST
        assert (
            InternalTypes.get_from_type(Union, (int, type(None)))
            == InternalTypes.OPTIONAL
        )
        assert (
            InternalTypes.get_from_type(InternalTestClass, ...) == InternalTypes.OBJECT
        )

    def test_get_struct_token(self) -> None:
        assert InternalTypes.BOOL.value.get_struct_token(True) == "<?"
        assert InternalTypes.INT_8.value.get_struct_token(True) == "<b"
        assert InternalTypes.INT_16.value.get_struct_token(True) == "<h"
        assert InternalTypes.INT_32.value.get_struct_token(True) == "<i"
        assert InternalTypes.INT_64.value.get_struct_token(True) == "<l"
        assert InternalTypes.UINT8.value.get_struct_token(True) == "<B"
        assert InternalTypes.UINT16.value.get_struct_token(True) == "<H"
        assert InternalTypes.UINT32.value.get_struct_token(True) == "<I"
        assert InternalTypes.UINT64.value.get_struct_token(True) == "<L"
        assert InternalTypes.UINT.value.get_struct_token(True) == "<I"
        assert InternalTypes.INT.value.get_struct_token(True) == "<i"
        assert InternalTypes.FLOAT.value.get_struct_token(True) == "<f"
        assert InternalTypes.DOUBLE.value.get_struct_token(True) == "<d"

    def test_get_python_type(self) -> None:
        assert InternalTypes.BOOL.value.get_python_type() is bool
        assert InternalTypes.INT_8.value.get_python_type() is int
        assert InternalTypes.INT_16.value.get_python_type() is int
        assert InternalTypes.INT_32.value.get_python_type() is int
        assert InternalTypes.INT_64.value.get_python_type() is int
        assert InternalTypes.UINT8.value.get_python_type() is int
        assert InternalTypes.UINT16.value.get_python_type() is int
        assert InternalTypes.UINT32.value.get_python_type() is int
        assert InternalTypes.UINT64.value.get_python_type() is int
        assert InternalTypes.UINT.value.get_python_type() is int
        assert InternalTypes.INT.value.get_python_type() is int
        assert InternalTypes.FLOAT.value.get_python_type() is float
        assert InternalTypes.DOUBLE.value.get_python_type() is float

    def test_custom_type(self) -> None:
        assert InternalTypes.STRING.value.get_python_type() is str
        assert InternalTypes.LIST.value.get_python_type() is list
        assert InternalTypes.OPTIONAL.value.get_python_type() is ...
        assert InternalTypes.OBJECT.value.get_python_type() is object
