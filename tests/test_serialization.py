from compacto import PROTOCOL_VERSION, inspect, pack, unpack
from compacto.encoding_headers import EncodingHeader
from compacto.utils.exceptions import InvalidHeaderException

import pytest
from pydantic import Field
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

    def test_pack_unpack_with_broken_api(self) -> None:
        @dataclass
        class Data1:
            a: int
            b: float

        @dataclass
        class Data2:
            b: float
            a: int

        obj = Data1(42, 3.14)
        data = pack(obj)

        with pytest.raises(InvalidHeaderException):
            _ = unpack(Data2, data)


class TestInspect:
    def test_inspect_bytes_returns_encoding_header(self) -> None:
        @dataclass
        class Point:
            x: float
            y: float

        data = pack(Point(1.0, 2.0))
        header = inspect(data)

        assert isinstance(header, EncodingHeader)

    def test_inspect_bytes_has_correct_version(self) -> None:
        @dataclass
        class Point:
            x: float
            y: float

        data = pack(Point(1.0, 2.0))
        header = inspect(data)

        assert header.version == PROTOCOL_VERSION

    def test_inspect_type_returns_encoding_header(self) -> None:
        @dataclass
        class Point:
            x: float
            y: float

        header = inspect(Point)

        assert isinstance(header, EncodingHeader)

    def test_inspect_type_has_correct_version(self) -> None:
        @dataclass
        class Point:
            x: float
            y: float

        header = inspect(Point)

        assert header.version == PROTOCOL_VERSION

    def test_inspect_type_and_bytes_yield_same_schema_hash(self) -> None:
        @dataclass
        class Point:
            x: float
            y: float

        data = pack(Point(1.0, 2.0))
        header_from_bytes = inspect(data)
        header_from_type = inspect(Point)

        assert header_from_bytes.schema_hash == header_from_type.schema_hash

    def test_inspect_different_structs_yield_different_schema_hashes(self) -> None:
        @dataclass
        class A:
            x: int

        @dataclass
        class B:
            x: float

        assert inspect(A).schema_hash != inspect(B).schema_hash

    def test_inspect_struct_field_order_affects_schema_hash(self) -> None:
        @dataclass
        class AB:
            a: int
            b: float

        @dataclass
        class BA:
            b: float
            a: int

        assert inspect(AB).schema_hash != inspect(BA).schema_hash

    def test_inspect_invalid_input_raises_type_error(self) -> None:
        with pytest.raises(TypeError):
            inspect(42)  # type: ignore[arg-type]

    def test_inspect_with_ctypes_annotation_differs_from_default(self) -> None:
        @dataclass
        class Precise:
            a: Annotated[int, ctypes.c_int16]

        @dataclass
        class Default:
            a: int

        assert inspect(Precise).schema_hash != inspect(Default).schema_hash

    def test_pack_unpack_truncated_before_header_ending(self):
        @dataclass
        class Default:
            a: int

        obj = Default(42)

        data = pack(obj)

        with pytest.raises(InvalidHeaderException):
            _ = unpack(Default, data[:3])

    def test_pack_unpack_compatibility_with_pydantic_without_precision(self):
        from pydantic import BaseModel

        class Data(BaseModel):
            a: Annotated[int, ctypes.c_int16] = Field(
                gt=0,
                lt=43,
                description="these field validations will not break or impact the serialization",
            )
            b: Annotated[float, ctypes.c_double] = Field(
                gt=0,
                lt=3.15,
                description="these field validations will not break or impact the serialization",
            )

        obj = Data(a=42, b=3.14)

        data = pack(obj)
        unpacked_obj = unpack(Data, data)

        assert obj.a == unpacked_obj.a
        assert obj.b == unpacked_obj.b

    def test_pack_unpack_compatibility_with_pydantic_with_precision(self):
        from pydantic import BaseModel

        class Data(BaseModel):
            a: int = Field(
                gt=0,
                lt=43,
                description="these field validations will not break or impact the serialization",
            )
            b: float = Field(
                gt=0,
                lt=3.15,
                description="these field validations will not break or impact the serialization",
            )

        obj = Data(a=42, b=3.14)

        data = pack(obj)
        unpacked_obj = unpack(Data, data)

        assert obj.a == unpacked_obj.a
        assert obj.b == unpacked_obj.b
