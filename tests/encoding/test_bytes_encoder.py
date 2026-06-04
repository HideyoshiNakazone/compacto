from compacto.encoding.bytes_encoder import ByteEncoder
from compacto.utils.constants import SIZE_UNSIGNED_LONG


class TestByteEncoder:
    def test_encode_decode_bytes(self):
        value = b"Hello World"

        data = ByteEncoder.encode(value)
        decoded_value, offset = ByteEncoder.decode(..., data)

        assert decoded_value == value

    def test_encode_decode_empty_bytes(self):
        value = b""

        data = ByteEncoder.encode(value)
        decoded_value, offset = ByteEncoder.decode(..., data)

        assert decoded_value == value

    def test_encode_returns_bytes(self):
        data = ByteEncoder.encode(b"test")

        assert isinstance(data, bytes)

    def test_decode_offset(self):
        value = b"test"
        data = ByteEncoder.encode(value)
        _, offset = ByteEncoder.decode(..., data)

        assert offset == SIZE_UNSIGNED_LONG + len(value)
