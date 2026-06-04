from compacto.internal_types import HasAnnotations, TreeNode

from typing_extensions import (
    Generic,
    Self,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from dataclasses import dataclass


T = TypeVar("T", bound=HasAnnotations)


class _GenericTypeDeff(Generic[T]):
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
class FallbackPickle(_GenericTypeDeff[T]):
    name: str


StructTyping = StructDeff | FieldsDeff | ListDeff | FallbackPickle


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
            TreeNode[StructTyping]
            .new(ListDeff(name=field_name))
            .add_child(_parse_type("_element", get_args(field_type)[0]))
        )

    if origin.__module__ == "builtins":
        return TreeNode[StructTyping].new(
            FieldsDeff(name=field_name, field_type=field_type)
        )

    annotated_fields = get_type_hints(field_type)
    if (
        annotated_fields is None
        or not _is_valid_annotation(field_type, annotated_fields)
        or not _is_buildable_class(field_type, annotated_fields)
    ):
        return TreeNode[StructTyping].new(FallbackPickle(name=field_name))

    struct_node = TreeNode[StructTyping].new(
        StructDeff(name=field_name, field_type=field_type, fields=annotated_fields)
    )
    for sub_field_name, sub_field_type in annotated_fields.items():
        struct_node.add_child(_parse_type(sub_field_name, sub_field_type))

    return struct_node


def struct_parser(obj_or_clzz: T | type[T]) -> TreeNode[StructTyping]:
    clzz = obj_or_clzz if isinstance(obj_or_clzz, type) else type(obj_or_clzz)
    return _parse_type(clzz.__name__, clzz)
