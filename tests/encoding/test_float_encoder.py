from compacto.encoding.float_encoder import FloatEncoder
from compacto.utils.constants import InternalTypes


SIZE_DOUBLE = InternalTypes.DOUBLE.get_byte_size()


class TestFloatEncoder:
    def test_encode_decode_positive_float(self):
        data = FloatEncoder.encode(..., 3.14)
        decoded_value, offset = FloatEncoder.decode(..., data)

        assert decoded_value == 3.14

    def test_encode_decode_negative_float(self):
        data = FloatEncoder.encode(..., -2.718)
        decoded_value, offset = FloatEncoder.decode(..., data)

        assert decoded_value == -2.718

    def test_encode_decode_zero(self):
        data = FloatEncoder.encode(..., 0.0)
        decoded_value, offset = FloatEncoder.decode(..., data)

        assert decoded_value == 0.0

    def test_encode_returns_bytes(self):
        data = FloatEncoder.encode(..., 1.0)

        assert isinstance(data, bytes)

    def test_decode_offset(self):
        data = FloatEncoder.encode(..., 1.0)
        _, offset = FloatEncoder.decode(..., data)

        assert offset == SIZE_DOUBLE
