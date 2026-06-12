from compacto.encoding.string_encoder import StringEncoder
from compacto.encoding_headers import OptionFlags


class TestStringEncoder:
    def test_encode_decode_string(self):
        string_value = "Hello World"

        data = StringEncoder._encode(..., string_value, OptionFlags.NONE)
        decoded_string, offset = StringEncoder._decode(..., data, OptionFlags.NONE)

        assert string_value == decoded_string

    def test_encode_decode_empty_string(self):
        string_value = ""

        data = StringEncoder._encode(..., string_value, OptionFlags.NONE)
        decoded_string, offset = StringEncoder._decode(..., data, OptionFlags.NONE)

        assert string_value == decoded_string

    def test_encode_decode_large_string(self):
        chunk_size_mb = 100
        chunk_string = "A" * (1024 * 1024 * chunk_size_mb)  # 100 MB block

        data = StringEncoder._encode(..., chunk_string, OptionFlags.NONE)
        decoded_string, offset = StringEncoder._decode(..., data, OptionFlags.NONE)

        assert chunk_string == decoded_string
