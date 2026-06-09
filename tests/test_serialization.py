from compacto import pack, unpack

from typing_extensions import Annotated, Optional

import ctypes
import sys
from dataclasses import dataclass


class TestSerialization:
    def test_pack_unpack(self) -> None:
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

    def test_pack_unpack_on_native_types(self) -> None:
        ORIGINAL_DATA = 42

        data = pack(ORIGINAL_DATA)
        unpacked_data = unpack(int, data)

        assert unpacked_data == ORIGINAL_DATA

    def test_pack_unpack_with_precision(self) -> None:
        @dataclass
        class Data:
            a: Annotated[int, ctypes.c_int16]
            b: Annotated[int, ctypes.c_int32]

        obj = Data(42, 100000)
        data = pack(obj)
        unpacked_obj = unpack(Data, data)

        assert unpacked_obj.a == obj.a
        assert unpacked_obj.b == obj.b

    def test_pack_has_lower_usage_with_precision(self) -> None:
        @dataclass
        class Data1:
            a: Annotated[int, ctypes.c_int16]
            b: Annotated[float, ctypes.c_float]

        @dataclass
        class Data2:
            a: int
            b: float

        obj1 = Data1(42, 3.14)
        obj2 = Data2(42, 3.14)

        data1 = pack(obj1)
        data2 = pack(obj2)

        assert sys.getsizeof(data1) < sys.getsizeof(data2)
