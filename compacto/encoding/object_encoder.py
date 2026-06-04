from compacto.encoding.type_encoder import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructDeff, StructTyping, struct_parser

from typing import Tuple


class ObjectEncoder(TypeEncoder[object]):
    mapped_type = object

    @staticmethod
    def encode(value: object) -> bytes:
        typing_tree = struct_parser(value)

        data = b""

        for node in typing_tree:
            if isinstance(node, StructDeff):
                continue

            encoder = TypeEncoder.get_implementation(node.field_type)
            if encoder is None:
                raise TypeError(f"Unsupported field type: {node.field_type}")

            data += encoder.encode(getattr(value, node.name))

        return data

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[object, int]:
        clzz: type = node.data.field_type

        typing_tree = struct_parser(clzz)

        fields: dict[str, object] = {}
        offset = 0

        for child_node in typing_tree:
            if isinstance(child_node, StructDeff):
                continue

            encoder = TypeEncoder.get_implementation(child_node.field_type)
            if encoder is None:
                raise TypeError(f"Unsupported field type: {child_node.field_type}")

            value, var_offset = encoder.decode(child_node.to_tree_node(), data[offset:])
            offset += var_offset
            fields[child_node.name] = value

        return clzz(**fields), offset
