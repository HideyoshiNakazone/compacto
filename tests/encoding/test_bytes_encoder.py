from compacto.encoding.bytes_encoder import ByteEncoder
from compacto.utils.constants import InternalTypes


SIZE_UNSIGNED_LONG_LONG = InternalTypes.UINT64.get_byte_size()


class TestByteEncoder:
    def test_encode_decode_bytes(self):
        value = b"Hello World"

        data = ByteEncoder._encode(..., value)
        decoded_value, offset = ByteEncoder._decode(..., data)

        assert decoded_value == value

    def test_encode_decode_empty_bytes(self):
        value = b""

        data = ByteEncoder._encode(..., value)
        decoded_value, offset = ByteEncoder._decode(..., data)

        assert decoded_value == value

    def test_encode_returns_bytes(self):
        data = ByteEncoder._encode(..., b"test")

        assert isinstance(data, bytes)

    def test_decode_offset(self):
        value = b"test"
        data = ByteEncoder._encode(..., value)
        _, offset = ByteEncoder._decode(..., data)

        assert offset == SIZE_UNSIGNED_LONG_LONG + len(value)
