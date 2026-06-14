from compacto.encoding import TypeEncoder
from compacto.encoding.field_encoder import FieldEncoder
from compacto.struct_parser import FieldsDeff
from compacto.utils.constants import InternalTypes
from compacto.utils.exceptions import AssertionException, DecodingException

import pytest

from enum import Enum
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

    def test_encode_wraps_exception_as_decoding_exception(self) -> None:
        node = FieldsDeff("test", InternalTypes.INT.value).to_tree_node()
        with pytest.raises(DecodingException):
            FieldEncoder.encode(node, "not_an_int")

    def test_decode_wraps_exception_as_decoding_exception(self) -> None:
        node = FieldsDeff("test", InternalTypes.INT.value).to_tree_node()
        with pytest.raises(DecodingException):
            FieldEncoder.decode(node, b"")  # too few bytes to unpack an int

    def test_init_subclass_raises_assertion_when_mapped_type_value_is_not_internal_type(
        self,
    ) -> None:
        class FakeEnum(Enum):
            FAKE = "not_an_internal_type"

        with pytest.raises(AssertionException):

            class BadEncoder(TypeEncoder):
                mapped_type = FakeEnum.FAKE

                def _encode(self, node, value, **options): ...

                def _decode(self, node, data, **options): ...
