from compacto.encoding_headers import InternalOptions

import pytest


@pytest.fixture
def default_options() -> InternalOptions:
    return InternalOptions(
        is_little_endian=False,
        is_8_byte_hash=False,
        is_length_64_bytes=False,
    )
