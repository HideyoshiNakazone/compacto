from compacto.encoding.bytes_encoder import ByteEncoder
from compacto.utils.constants import InternalTypes


SIZE_UNSIGNED_LONG_LONG = InternalTypes.UINT64.get_byte_size(False)


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
