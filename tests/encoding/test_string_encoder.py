from compacto.encoding.string_encoder import StringEncoder


class TestStringEncoder:
    def test_encode_decode_string(self):
        string_value = "Hello World"

        data = StringEncoder._encode(..., string_value)
        decoded_string, offset = StringEncoder._decode(..., data)

        assert string_value == decoded_string

    def test_encode_decode_empty_string(self):
        string_value = ""

        data = StringEncoder._encode(..., string_value)
        decoded_string, offset = StringEncoder._decode(..., data)

        assert string_value == decoded_string

    def test_encode_decode_large_string(self):
        chunk_size_mb = 100
        chunk_string = "A" * (1024 * 1024 * chunk_size_mb)  # 100 MB block

        data = StringEncoder._encode(..., chunk_string)
        decoded_string, offset = StringEncoder._decode(..., data)

        assert chunk_string == decoded_string
