from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import (
    ObjectDeff,
    StructTyping,
    struct_parser,
)
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import Buffer, Tuple, Unpack


class ObjectEncoder(TypeEncoder):
    mapped_type = InternalTypes.OBJECT

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping], value: object, **options: Unpack[InternalOptions]
    ) -> Buffer:
        data = bytearray()
        for child_node in node:
            data.extend(
                TypeEncoder.pack(
                    child_node, getattr(value, child_node.data.field_name), **options
                )
            )

        return data

    @staticmethod
    def _decode(
        node: TreeNode[ObjectDeff], data: Buffer, **options: Unpack[InternalOptions]
    ) -> Tuple[object, int]:
        typing_tree = struct_parser(node.data.field_clzz)

        fields: dict[str, object] = {}
        offset = 0

        for child_node in typing_tree:
            value, var_offset = TypeEncoder.unpack(child_node, data[offset:], **options)
            offset += var_offset
            fields[child_node.data.field_name] = value

        return node.data.field_clzz(**fields), offset
