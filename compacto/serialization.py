from compacto.internal_types import HasAnnotations
from compacto.struct_parser import StructDeff, struct_parser

import struct
from typing import TypeVar


T = TypeVar("T", bound=HasAnnotations)


def pack(obj: T) -> bytes:
    typing_tree = struct_parser(obj)

    data = b""

    for node in typing_tree:
        if isinstance(node, StructDeff):
            continue

        if node.field_type is int:
            data += struct.pack("i", getattr(obj, node.name))

        if node.field_type is str:
            encoded_str = getattr(obj, node.name).encode("utf-8")
            data += struct.pack("I", len(encoded_str))  # length prefix
            data += encoded_str

        if node.field_type is bool:
            data += struct.pack("?", getattr(obj, node.name))

        if node.field_type is float:
            data += struct.pack("f", getattr(obj, node.name))

        if node.field_type is bytes:
            byte_data = getattr(obj, node.name)
            data += struct.pack("I", len(byte_data))  # length prefix
            data += byte_data

    return data


def unpack(clzz: type[T], data: bytes) -> T:
    typing_tree = struct_parser(clzz)
    fields: dict[str, object] = {}
    offset = 0

    for node in typing_tree:
        if isinstance(node, StructDeff):
            continue

        if node.field_type is int:
            (value,) = struct.unpack_from("i", data, offset)
            offset += struct.calcsize("i")
            fields[node.name] = value

        elif node.field_type is str:
            (length,) = struct.unpack_from("I", data, offset)
            offset += struct.calcsize("I")
            fields[node.name] = data[offset : offset + length].decode("utf-8")
            offset += length

        elif node.field_type is bool:
            (value,) = struct.unpack_from("?", data, offset)
            offset += struct.calcsize("?")
            fields[node.name] = value

        elif node.field_type is float:
            (value,) = struct.unpack_from("f", data, offset)
            offset += struct.calcsize("f")
            fields[node.name] = value

        elif node.field_type is bytes:
            (length,) = struct.unpack_from("I", data, offset)
            offset += struct.calcsize("I")
            fields[node.name] = data[offset : offset + length]
            offset += length

    return clzz(**fields)
