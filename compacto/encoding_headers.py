from compacto.struct_parser import FieldsDeff, StructTyping
from compacto.utils.exceptions import InvalidHeaderException
from compacto.utils.tree_node import TreeNode

from typing_extensions import Self

import ctypes
import hashlib
import struct
from dataclasses import dataclass
from enum import IntFlag


HEADER_ENDIAN = ">"


class OptionFlags(IntFlag):
    NONE = 0
    IS_LITTLE_ENDIAN = 1 << 1
    IS_8_BYTE_HASH = 1 << 2
    IS_COMPRESSED = 1 << 3


ENCODING_HASH_SIZE = 4


OPTIONS_ENCODING_TOKEN = f"{HEADER_ENDIAN}{ctypes.c_uint16._type_}"
OPTIONS_ENCODING_SIZE = struct.calcsize(OPTIONS_ENCODING_TOKEN)


VERSION_ENCODING_TOKEN = f"{HEADER_ENDIAN}{ctypes.c_uint16._type_}"
VERSION_BYTES_SIZE = struct.calcsize(VERSION_ENCODING_TOKEN)


def get_hash_token(options: OptionFlags) -> str:
    token = (
        ctypes.c_uint64._type_
        if OptionFlags.IS_8_BYTE_HASH in options
        else ctypes.c_uint32._type_
    )
    return f"{HEADER_ENDIAN}{token}"


def get_hash_size(options: OptionFlags) -> int:
    token = get_hash_token(options)
    return struct.calcsize(token)


"""
Compacto Header Layout
======================

The header is ALWAYS encoded using HEADER_ENDIAN (currently big-endian '>'),
regardless of the payload endianness.

This guarantees that the decoder can always read the header deterministically
without first needing to inspect any flags.

Header Layout:

    +----------+----------+-------------+
    | Options  | Version  | Schema Hash |
    +----------+----------+-------------+
    |  uint16  |  uint16  | 4B or 8B    |
    +----------+----------+-------------+
         2B         2B      variable

Byte Offsets:

    0x00  0x01  | Options (uint16)
    0x02  0x03  | Version (uint16)
    0x04  ...   | Schema Hash

Options Flags:

    Bit 1 (0x0002) -> IS_LITTLE_ENDIAN
    Bit 2 (0x0004) -> IS_8_BYTE_HASH
    Bit 3 (0x0008) -> IS_COMPRESSED

Notes:

- The header is always decoded using HEADER_ENDIAN.
- IS_LITTLE_ENDIAN affects ONLY the payload encoding.
- Schema Hash size is determined by IS_8_BYTE_HASH.
- Additional flags may be added in future protocol versions.
- Unknown flags should be ignored when possible to preserve
  forward compatibility.

Example:

    Header (big-endian):
    +----------+----------+-------------+
    | 0x0002   | 0x0001   | hash bytes  |
    +----------+----------+-------------+

    Options = IS_LITTLE_ENDIAN
    Version = 1

    The payload following the header is encoded using little-endian,
    but the header itself remains big-endian.
"""


def calc_hash_from_tree(typing_tree: TreeNode[StructTyping], digest_size: int) -> bytes:
    h = hashlib.blake2b(digest_size=digest_size)

    deff = typing_tree.data
    h.update(type(deff).__name__.encode())
    h.update(deff.field_name.encode())

    if isinstance(deff, FieldsDeff):
        h.update(deff.field_impl.ctype.__name__.encode())

    for child in typing_tree.children:
        h.update(calc_hash_from_tree(child, digest_size))

    return h.digest()


@dataclass(slots=True)
class EncodingHeader:
    options: OptionFlags
    version: int
    schema_hash: bytes

    def encode(self) -> bytearray:
        data = bytearray()

        data.extend(struct.pack(OPTIONS_ENCODING_TOKEN, int(self.options)))
        data.extend(struct.pack(VERSION_ENCODING_TOKEN, self.version))
        data.extend(self.schema_hash)

        return data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        minimum_size = (
            OPTIONS_ENCODING_SIZE
            + VERSION_BYTES_SIZE
            + struct.calcsize(f"{HEADER_ENDIAN}{ctypes.c_uint32._type_}")
        )

        if len(data) < minimum_size:
            raise InvalidHeaderException("Invalid encoding header. Data is too small.")

        offset = 0

        options = OptionFlags(
            struct.unpack(
                OPTIONS_ENCODING_TOKEN,
                data[offset : offset + OPTIONS_ENCODING_SIZE],
            )[0]
        )
        offset += OPTIONS_ENCODING_SIZE

        version = struct.unpack(
            VERSION_ENCODING_TOKEN,
            data[offset : offset + VERSION_BYTES_SIZE],
        )[0]
        offset += VERSION_BYTES_SIZE

        hash_size = get_hash_size(options)
        expected_size = OPTIONS_ENCODING_SIZE + VERSION_BYTES_SIZE + hash_size

        if len(data) < expected_size:
            raise InvalidHeaderException(
                "Invalid encoding header. Missing schema hash bytes."
            )

        schema_hash = data[offset : offset + hash_size]

        return cls(
            options=options,
            version=version,
            schema_hash=schema_hash,
        )

    @classmethod
    def from_params(
        cls,
        version: int,
        options: OptionFlags,
        typing_tree: TreeNode[StructTyping],
    ) -> Self:
        hash_size = get_hash_size(options)

        schema_hash = calc_hash_from_tree(
            typing_tree,
            digest_size=hash_size,
        )

        return cls(
            options=options,
            version=version,
            schema_hash=schema_hash,
        )

    @property
    def size_of_header(self) -> int:
        return OPTIONS_ENCODING_SIZE + VERSION_BYTES_SIZE + len(self.schema_hash)
