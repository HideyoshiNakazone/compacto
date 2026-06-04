from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import (
    FallbackPickle,
    StructTyping,
    struct_parser,
)
from compacto.utils.constants import SIZE_LONG_LONG, UNSIGNED_LONG_TYPE_TOKEN

import pickle
import struct
from typing import Tuple


class ObjectEncoder(TypeEncoder[object]):
    mapped_type = object

    @staticmethod
    def encode(value: object) -> bytes:
        typing_tree = struct_parser(value)

        if isinstance(typing_tree.data, FallbackPickle):
            data = pickle.dumps(value)
            len_data = len(data)
            return struct.pack(UNSIGNED_LONG_TYPE_TOKEN, len_data) + data

        data = b""
        for node in typing_tree:
            node_data = node.data
            encoder = TypeEncoder.get_implementation(node_data.field_type)
            if encoder is None:
                raise TypeError(f"Unsupported field type: {node_data.field_type}")

            data += encoder.encode(getattr(value, node_data.name))

        return data

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[object, int]:
        clzz: type = node.data.field_type

        typing_tree = struct_parser(clzz)

        if isinstance(typing_tree.data, FallbackPickle):
            (len_data,) = struct.unpack_from(UNSIGNED_LONG_TYPE_TOKEN, data)
            data = pickle.loads(data[SIZE_LONG_LONG:len_data])
            return data, SIZE_LONG_LONG + len_data

        fields: dict[str, object] = {}
        offset = 0

        for child_node in typing_tree:
            node_data = child_node.data
            encoder = TypeEncoder.get_implementation(node_data.field_type)
            if encoder is None:
                raise TypeError(f"Unsupported field type: {node_data.field_type}")

            value, var_offset = encoder.decode(child_node, data[offset:])
            offset += var_offset
            fields[node_data.name] = value

        return clzz(**fields), offset
