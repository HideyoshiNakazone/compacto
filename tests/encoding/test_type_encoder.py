from compacto.encoding import TypeEncoder

import pytest

from types import EllipsisType


class TestTypeEncoder:
    def test_can_get_bool_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(bool)
        assert encoder.mapped_type is bool

    def test_can_get_bytes_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(bytes)
        assert encoder.mapped_type is bytes

    def test_can_get_float_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(float)
        assert encoder.mapped_type is float

    def test_can_get_int_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(int)
        assert encoder.mapped_type is int

    def test_can_get_list_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(list)
        assert encoder.mapped_type is list

    def test_can_get_object_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(object)
        assert encoder.mapped_type is object

    def test_can_get_str_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(str)
        assert encoder.mapped_type is str

    def test_cannot_get_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(EllipsisType)
        assert encoder.mapped_type is object

    def test_raises_if_subclass_doesnt_have_mapped_type(self) -> None:
        with pytest.raises(TypeError):

            class InvalidTypeEncoder(TypeEncoder):
                def encode(self, obj: EllipsisType) -> bytes: ...

                def decode(self, obj: bytes) -> EllipsisType: ...
