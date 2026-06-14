from compacto.encoding_headers import EncodingHeader, InternalOptions, OptionFlags
from compacto.utils.exceptions import InvalidHeaderException

import pytest


class TestOptionFlags:
    def test_from_internal_options_no_flags(self) -> None:
        options = InternalOptions(
            is_little_endian=False, is_8_byte_hash=False, is_length_64_bytes=False
        )
        flags = OptionFlags.from_internal_options(options)
        assert flags == OptionFlags.NONE

    def test_from_internal_options_is_little_endian(self) -> None:
        options = InternalOptions(
            is_little_endian=True, is_8_byte_hash=False, is_length_64_bytes=False
        )
        flags = OptionFlags.from_internal_options(options)
        assert OptionFlags.IS_LITTLE_ENDIAN in flags

    def test_from_internal_options_is_8_byte_hash(self) -> None:
        options = InternalOptions(
            is_little_endian=False, is_8_byte_hash=True, is_length_64_bytes=False
        )
        flags = OptionFlags.from_internal_options(options)
        assert OptionFlags.IS_8_BYTE_HASH in flags

    def test_from_internal_options_is_length_64_bytes(self) -> None:
        options = InternalOptions(
            is_little_endian=False, is_8_byte_hash=False, is_length_64_bytes=True
        )
        flags = OptionFlags.from_internal_options(options)
        assert OptionFlags.IS_LENGTH_64_BYTES in flags

    def test_from_internal_options_all_flags(self) -> None:
        options = InternalOptions(
            is_little_endian=True, is_8_byte_hash=True, is_length_64_bytes=True
        )
        flags = OptionFlags.from_internal_options(options)
        assert OptionFlags.IS_LITTLE_ENDIAN in flags
        assert OptionFlags.IS_8_BYTE_HASH in flags
        assert OptionFlags.IS_LENGTH_64_BYTES in flags


class TestEncodingHeaderDecode:
    def test_decode_raises_when_data_too_small(self) -> None:
        with pytest.raises(InvalidHeaderException, match="Data is too small"):
            EncodingHeader.decode(b"\x00" * 3)
