from compacto.encoding import (
    TypeEncoder,
)
from compacto.encoding_headers import EncodingHeader
from compacto.struct_parser import struct_parser
from compacto.utils.annotations import HasAnnotations
from compacto.utils.exceptions import InvalidHeaderException

from typing_extensions import TypeVar


PROTOCOL_VERSION = 1


T = TypeVar("T", bound=HasAnnotations)


def inspect(pos_data: type[T] | bytes) -> EncodingHeader:
    if isinstance(pos_data, (bytes, bytearray, memoryview)):
        return EncodingHeader.decode(pos_data)

    if not isinstance(pos_data, type):
        raise TypeError("Expected a type or bytes data for inspection.")

    typing_tree = struct_parser(pos_data)
    return EncodingHeader.from_params(PROTOCOL_VERSION, typing_tree)


def pack(obj: T) -> bytes:
    typing_tree = struct_parser(type(obj))
    header = EncodingHeader.from_params(PROTOCOL_VERSION, typing_tree)
    encoded_data = TypeEncoder.pack(typing_tree, obj)

    out = bytearray(header.size_of_header + len(encoded_data))
    out[: header.size_of_header] = header.encode()
    out[header.size_of_header :] = encoded_data
    return bytes(out)


def unpack(clzz: type[T], data: bytes) -> T:
    typing_tree = struct_parser(clzz)
    header = EncodingHeader.decode(data)

    expected = EncodingHeader.from_params(PROTOCOL_VERSION, typing_tree)

    if header.version != expected.version:
        raise InvalidHeaderException(
            f"Protocol version mismatch: expected {expected.version}, got {header.version}"
        )

    if header.schema_hash != expected.schema_hash:
        raise InvalidHeaderException(
            "Schema mismatch: the binary data was encoded with a different struct layout."
        )

    value, _ = TypeEncoder.unpack(typing_tree, data[header.size_of_header :])
    return value
