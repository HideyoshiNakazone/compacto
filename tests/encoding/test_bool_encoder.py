from compacto.encoding.bool_encoder import BoolEncoder
from compacto.utils.constants import SIZE_BOOL


class TestBoolEncoder:
    def test_encode_decode_true(self):
        data = BoolEncoder.encode(True)
        decoded_value, offset = BoolEncoder.decode(..., data)

        assert decoded_value is True

    def test_encode_decode_false(self):
        data = BoolEncoder.encode(False)
        decoded_value, offset = BoolEncoder.decode(..., data)

        assert decoded_value is False

    def test_encode_returns_bytes(self):
        data = BoolEncoder.encode(True)

        assert isinstance(data, bytes)

    def test_decode_offset(self):
        data = BoolEncoder.encode(True)
        _, offset = BoolEncoder.decode(..., data)

        assert offset == SIZE_BOOL
