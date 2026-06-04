from compacto import pack, unpack

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

    obj = DataWrapper(42, "teste", ["a", "b", "c"], SubData(1, 2))
    data = pack(obj)

    unpacked_obj = unpack(DataWrapper, data)

    assert unpacked_obj.a == obj.a
    assert unpacked_obj.b == obj.b
    assert unpacked_obj.c == obj.c
    assert unpacked_obj.d == obj.d
