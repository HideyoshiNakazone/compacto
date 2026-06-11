from compacto.encoding import TypeEncoder
from compacto.utils.constants import InternalTypes

import pytest

from types import EllipsisType


class TestTypeEncoder:
    def test_can_get_bool_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(InternalTypes.ANY_CTYPE)
        assert encoder.mapped_type is InternalTypes.ANY_CTYPE

    def test_can_get_bytes_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(InternalTypes.BYTES)
        assert encoder.mapped_type is InternalTypes.BYTES

    def test_can_get_list_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(InternalTypes.LIST)
        assert encoder.mapped_type is InternalTypes.LIST

    def test_can_get_object_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(InternalTypes.OBJECT)
        assert encoder.mapped_type is InternalTypes.OBJECT

    def test_can_get_str_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(InternalTypes.STRING)
        assert encoder.mapped_type is InternalTypes.STRING

    def test_cannot_get_implementation(self) -> None:
        encoder = TypeEncoder.get_implementation(...)
        assert encoder.mapped_type == InternalTypes.OBJECT

    def test_raises_if_subclass_doesnt_have_mapped_type(self) -> None:
        with pytest.raises(TypeError):

            class InvalidTypeEncoder(TypeEncoder):
                def _encode(self, obj: EllipsisType) -> bytes: ...

                def _decode(self, obj: bytes) -> EllipsisType: ...
