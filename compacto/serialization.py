from compacto.encoding import BoolEncoder, FloatEncoder, IntEncoder, StringEncoder
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
            data += IntEncoder.encode(getattr(obj, node.name))

        if node.field_type is str:
            data += StringEncoder.encode(getattr(obj, node.name))

        if node.field_type is bool:
            data += BoolEncoder.encode(getattr(obj, node.name))

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
            value, var_offset = IntEncoder.decode(data[offset:])
            offset += var_offset
            fields[node.name] = value

        elif node.field_type is str:
            value, var_offset = StringEncoder.decode(data[offset:])
            offset += var_offset
            fields[node.name] = value

        elif node.field_type is bool:
            value, var_offset = BoolEncoder.decode(data[offset:])
            offset += var_offset
            fields[node.name] = value

        elif node.field_type is float:
            value, var_offset = FloatEncoder.decode(data[offset:])
            offset += var_offset
            fields[node.name] = value

        elif node.field_type is bytes:
            (length,) = struct.unpack_from("I", data, offset)
            offset += struct.calcsize("I")
            fields[node.name] = data[offset : offset + length]
            offset += length

    return clzz(**fields)
