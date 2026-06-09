from compacto.encoding.type_encoder import TypeEncoder
from compacto.struct_parser import (
    ObjectDeff,
    StructTyping,
    struct_parser,
)
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple


class ObjectEncoder(TypeEncoder):
    mapped_type = InternalTypes.OBJECT

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: object) -> bytes:
        data = bytearray()
        for child_node in node:
            data.extend(
                TypeEncoder.pack(child_node, getattr(value, child_node.data.field_name))
            )

        return data

    @staticmethod
    def decode(node: TreeNode[ObjectDeff], data: bytes) -> Tuple[object, int]:
        typing_tree = struct_parser(node.data.field_clzz)

        fields: dict[str, object] = {}
        offset = 0

        for child_node in typing_tree:
            value, var_offset = TypeEncoder.unpack(child_node, data[offset:])
            offset += var_offset
            fields[child_node.data.field_name] = value

        return node.data.field_clzz(**fields), offset
