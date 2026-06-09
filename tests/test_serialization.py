from compacto import pack, unpack

from typing_extensions import Annotated, Optional

import ctypes
from dataclasses import dataclass


def test_pack_unpack() -> None:
    @dataclass
    class SubData:
        a: int
        b: int

    @dataclass
    class DataWrapper:
        a: int
        b: str
        c: list[str]

        d: SubData
        e: Optional[SubData]

    obj = DataWrapper(42, "teste", ["a", "b", "c"], SubData(1, 2), None)
    data = pack(obj)

    unpacked_obj = unpack(DataWrapper, data)

    assert unpacked_obj.a == obj.a
    assert unpacked_obj.b == obj.b
    assert unpacked_obj.c == obj.c
    assert unpacked_obj.d == obj.d
    assert unpacked_obj.e == obj.e


def test_pack_unpack_on_native_types() -> None:
    ORIGINAL_DATA = 42

    data = pack(ORIGINAL_DATA)
    unpacked_data = unpack(int, data)

    assert unpacked_data == ORIGINAL_DATA


def test_pack_unpack_with_precision() -> None:
    @dataclass
    class Data:
        a: Annotated[int, ctypes.c_int16]
        b: Annotated[int, ctypes.c_int32]

    obj = Data(42, 100000)
    data = pack(obj)
    unpacked_obj = unpack(Data, data)

    assert unpacked_obj.a == obj.a
    assert unpacked_obj.b == obj.b
