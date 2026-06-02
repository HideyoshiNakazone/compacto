from encoding.int_encoder import IntEncoder


class TestIntEncoder:
    def test_encode_decode_int(self):
        int_value = 42

        data = IntEncoder.encode(int_value)
        decoded_int, offset = IntEncoder.decode(data)

        assert int_value == decoded_int

    def test_encode_decode_zero(self):
        int_value = 0

        data = IntEncoder.encode(int_value)
        decoded_int, offset = IntEncoder.decode(data)

        assert int_value == decoded_int

    def test_encode_decode_large_int(self):
        int_value = 2**63 - 1  # max signed 64-bit int

        data = IntEncoder.encode(int_value)
        decoded_int, offset = IntEncoder.decode(data)

        assert int_value == decoded_int

    def test_encode_decode_negative_int(self):
        int_value = -1

        data = IntEncoder.encode(int_value)
        decoded_int, offset = IntEncoder.decode(data)

        assert int_value == decoded_int
