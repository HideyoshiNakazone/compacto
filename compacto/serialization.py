from compacto.encoding import (
    TypeEncoder,
)
from compacto.encoding_headers import EncodingHeader, InternalOptions
from compacto.struct_parser import struct_parser
from compacto.utils.annotations import HasAnnotations
from compacto.utils.exceptions import InvalidHeaderException

from typing_extensions import TypeVar, Unpack


PROTOCOL_VERSION = 1


T = TypeVar("T", bound=HasAnnotations)


def inspect(pos_data: type[T] | bytes) -> EncodingHeader:
    """Return the encoding header for a type or encoded bytes.

    When given a type, builds the header from its struct layout.
    When given bytes, decodes the header from the binary data.
    """
    if isinstance(pos_data, (bytes, bytearray, memoryview)):
        return EncodingHeader.decode(pos_data)

    if not isinstance(pos_data, type):
        raise TypeError("Expected a type or bytes data for inspection.")

    typing_tree = struct_parser(pos_data)
    return EncodingHeader.from_params(PROTOCOL_VERSION, typing_tree)


def pack(obj: T, **kwargs: Unpack[InternalOptions]) -> bytes:
    """Serialize an annotated struct instance to bytes.

    Encodes the object preceded by a header containing the protocol version,
    schema hash, and encoding options derived from ``kwargs``.
    """
    typing_tree = struct_parser(type(obj))
    header = EncodingHeader.from_params(PROTOCOL_VERSION, typing_tree, **kwargs)
    encoded_data = TypeEncoder.pack(
        typing_tree, obj, **header.options.to_internal_options()
    )

    out = bytearray(header.size_of_header + len(encoded_data))
    out[: header.size_of_header] = header.encode()
    out[header.size_of_header :] = encoded_data
    return bytes(out)


def unpack(clzz: type[T], data: bytes) -> T:
    """Deserialize bytes into an instance of ``clzz``.

    Validates that the embedded header matches the expected protocol version
    and schema hash before decoding, raising ``InvalidHeaderException`` on
    any mismatch.
    """
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

    value, _ = TypeEncoder.unpack(
        typing_tree,
        data[header.size_of_header :],
        **header.options.to_internal_options(),
    )
    return value
