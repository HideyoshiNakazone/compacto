from compacto.internal_types import HasAnnotations, TreeNode

from typing_extensions import (
    Generic,
    Optional,
    Self,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from dataclasses import dataclass
from types import NoneType


T = TypeVar("T", bound=HasAnnotations)


class _GenericTypeDeff(Generic[T]):
    name: str
    field_type: type

    def to_tree_node(self) -> TreeNode[Self]:
        return TreeNode[StructTyping].new(self)


@dataclass
class StructDeff(_GenericTypeDeff[T]):
    name: str
    field_type: type
    fields: dict[str, type]


@dataclass
class ListDeff(_GenericTypeDeff[T]):
    name: str
    field_type: type = list


@dataclass
class FieldsDeff(_GenericTypeDeff[T]):
    name: str
    field_type: type


@dataclass
class OptionalDeff(_GenericTypeDeff[T]):
    name: str
    field_type = Optional


StructTyping = StructDeff | FieldsDeff | ListDeff


def _get_origin_type(field_type: type) -> type:
    """Unwrap generic aliases like list[int] → list."""
    return get_origin(field_type) or field_type


def _is_valid_annotation(clzz: type[T], annotations: dict[str, type] | None) -> bool:
    if annotations is None:
        return False

    all_attrs = [
        attr
        for attr in dir(clzz)
        if not attr.startswith("__") and not callable(getattr(clzz, attr))
    ]
    for field in all_attrs:
        if field not in annotations:
            return False

    return True


def _is_buildable_class(clzz: type[T], annotations: dict[str, type] | None) -> bool:
    if annotations is None:
        return False

    constructor_annotations = get_type_hints(clzz.__init__)
    if constructor_annotations is None:
        return False

    return all(
        (field in annotations)
        for field in constructor_annotations.keys()
        if field != "return"
    )


def _parse_type(field_name: str, field_type: type) -> TreeNode[StructTyping]:
    origin = _get_origin_type(field_type)

    if origin is list:
        return (
            ListDeff(name=field_name)
            .to_tree_node()
            .add_child(_parse_type("_element", get_args(field_type)[0]))
        )

    if (
        origin is Union
        and len(type_args := get_args(field_type)) == 2
        and type_args[1] is NoneType
    ):
        return (
            OptionalDeff(name=field_name)
            .to_tree_node()
            .add_child(_parse_type("_element", type_args[0]))
        )

    if origin is dict:
        raise TypeError(
            f"Dict types are not supported for field '{field_name}'. Consider using a list of key-value pairs instead."
        )

    if origin.__module__ == "builtins":
        return FieldsDeff(name=field_name, field_type=field_type).to_tree_node()

    annotated_fields = get_type_hints(field_type)
    if (
        annotated_fields is None
        or not _is_valid_annotation(field_type, annotated_fields)
        or not _is_buildable_class(field_type, annotated_fields)
    ):
        raise TypeError(
            "The provided type or doesn't have a __annotations__ attribute or doesn't have a compatible __init__ method. "
            "Ensure that all fields are annotated and that the class can be instantiated with those fields."
        )

    struct_node = StructDeff(
        name=field_name, field_type=field_type, fields=annotated_fields
    ).to_tree_node()
    for sub_field_name, sub_field_type in annotated_fields.items():
        struct_node.add_child(_parse_type(sub_field_name, sub_field_type))

    return struct_node


def struct_parser(obj_or_clzz: T | type[T]) -> TreeNode[StructTyping]:
    clzz = obj_or_clzz if isinstance(obj_or_clzz, type) else type(obj_or_clzz)
    return _parse_type(clzz.__name__, clzz)
