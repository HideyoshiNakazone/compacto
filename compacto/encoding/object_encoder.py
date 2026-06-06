from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import (
    StructTyping,
    struct_parser,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple


class ObjectEncoder(TypeEncoder[object]):
    mapped_type = object

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: object) -> bytes:
        data = bytearray()
        for child_node in node:
            node_data = child_node.data
            encoder = TypeEncoder.get_implementation(node_data.field_type)
            if encoder is None:
                raise TypeError(f"Unsupported field type: {node_data.field_type}")

            data.extend(encoder.encode(child_node, getattr(value, node_data.name)))

        return data

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[object, int]:
        clzz: type = node.data.field_type

        typing_tree = struct_parser(clzz)

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
