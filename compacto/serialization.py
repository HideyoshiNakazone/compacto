from compacto.encoding import (
    TypeEncoder,
)
from compacto.internal_types import HasAnnotations
from compacto.struct_parser import StructDeff, struct_parser

from typing import TypeVar


T = TypeVar("T", bound=HasAnnotations)


def pack(obj: T) -> bytes:
    typing_tree = struct_parser(obj)

    data = b""

    for node in typing_tree:
        if isinstance(node, StructDeff):
            continue

        encoder = TypeEncoder.get_implementation(node.field_type)
        if encoder is None:
            raise TypeError(f"Unsupported field type: {node.field_type}")

        data += encoder.encode(getattr(obj, node.name))

    return data


def unpack(clzz: type[T], data: bytes) -> T:
    typing_tree = struct_parser(clzz)
    fields: dict[str, object] = {}
    offset = 0

    for node in typing_tree:
        if isinstance(node, StructDeff):
            continue

        encoder = TypeEncoder.get_implementation(node.field_type)
        if encoder is None:
            raise TypeError(f"Unsupported field type: {node.field_type}")

        value, var_offset = encoder.decode(node, data[offset:])
        offset += var_offset
        fields[node.name] = value

    return clzz(**fields)
