from compacto.internal_types import HasAnnotations, TreeNode

import typing
from dataclasses import dataclass
from typing import TypeVar, get_type_hints


T = TypeVar("T", bound=HasAnnotations)


@dataclass
class StructDeff:
    name: str
    native_type: type
    fields: dict[str, type]


@dataclass
class FieldsDeff:
    name: str
    field_type: type


StructTyping = StructDeff | FieldsDeff


def get_origin_type(field_type: type) -> type:
    """Unwrap generic aliases like list[int] → list."""
    return typing.get_origin(field_type) or field_type


def struct_parser(obj_or_clzz: T | type[T]) -> TreeNode[StructTyping]:
    clzz = obj_or_clzz if isinstance(obj_or_clzz, type) else type(obj_or_clzz)

    annotated_fields = get_type_hints(clzz)
    if not annotated_fields:
        raise TypeError("Expected clzz to have a __annotations__ attribute")

    all_attrs = [
        attr
        for attr in dir(clzz)
        if not attr.startswith("__") and not callable(getattr(clzz, attr))
    ]
    for field in all_attrs:
        if field not in annotated_fields:
            raise TypeError(f"Field {field} not in {annotated_fields}")

    struct_node = TreeNode[StructTyping].new(
        StructDeff(name=clzz.__name__, native_type=clzz, fields=annotated_fields)
    )
    for field, field_type in annotated_fields.items():
        origin = get_origin_type(field_type)
        if origin.__module__ == "builtins":
            struct_node.add_child(
                TreeNode.new(FieldsDeff(name=field, field_type=field_type))
            )
        else:
            struct_node.add_child(struct_parser(clzz))

    return struct_node
