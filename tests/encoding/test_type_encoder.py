from compacto.encoding import TypeEncoder

import pytest

from types import EllipsisType


class TestTypeEncoder:
    def test_can_get_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(str)
        assert encoder.mapped_type is str

    def test_cannot_get_implementation(self) -> None:
        with pytest.raises(TypeError):
            _ = TypeEncoder.get_implementation(EllipsisType)

    def test_raises_if_subclass_doesnt_have_mapped_type(self) -> None:
        with pytest.raises(TypeError):

            class InvalidTypeEncoder(TypeEncoder):
                def encode(self, obj: EllipsisType) -> bytes: ...

                def decode(self, obj: bytes) -> EllipsisType: ...
