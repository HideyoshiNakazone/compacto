from compacto.encoding_headers import InternalOptions

import pytest


@pytest.fixture
def options() -> InternalOptions:
    return InternalOptions(
        is_little_endian=True,
        is_8_byte_hash=False,
        is_compressed=False,
    )
