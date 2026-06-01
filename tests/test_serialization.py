from compacto import pack, unpack

from dataclasses import dataclass


def test_pack_unpack() -> None:
    @dataclass
    class DataWrapper:
        a: int
        b: str

    obj = DataWrapper(42, "teste")
    data = pack(obj)

    unpacked_obj = unpack(DataWrapper, data)

    assert unpacked_obj.a == obj.a
    assert unpacked_obj.b == obj.b
