from compacto.utils.annotations import HasAnnotations
from compacto.utils.constants import Ctype, InternalType, InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import TypeVar, Union, get_args, get_origin, get_type_hints

from dataclasses import dataclass


T = TypeVar("T", bound=HasAnnotations)

K = TypeVar("K")


class _GenericTypeDeff:
    field_name: str
    field_type: InternalType

    def to_tree_node(self) -> TreeNode:
        return TreeNode.new(self)


@dataclass
class BytesDeff(_GenericTypeDeff):
    field_name: str
    field_type = InternalTypes.BYTES


@dataclass
class StringDeff(_GenericTypeDeff):
    field_name: str
    field_type = InternalTypes.STRING


@dataclass
class ListDeff(_GenericTypeDeff):
    field_name: str
    field_type = InternalTypes.LIST


@dataclass
class OptionalDeff(_GenericTypeDeff):
    field_name: str
    field_type = InternalTypes.OPTIONAL


@dataclass
class ObjectDeff(_GenericTypeDeff):
    field_name: str
    field_clzz: type
    fields: dict[str, type]
    field_type = InternalTypes.OBJECT


@dataclass
class FieldsDeff(_GenericTypeDeff):
    field_name: str
    field_impl: Ctype
    field_type = InternalTypes.ANY_CTYPE


StructTyping = Union[
    BytesDeff, StringDeff, ListDeff, OptionalDeff, ObjectDeff, FieldsDeff
]


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
    type_args = get_args(field_type)

    internal_type = InternalTypes.get_from_type(origin, type_args)

    match internal_type:
        case InternalTypes.BYTES:
            return BytesDeff(field_name=field_name).to_tree_node()

        case InternalTypes.STRING:
            return StringDeff(field_name=field_name).to_tree_node()

        case InternalTypes.LIST:
            return (
                ListDeff(field_name=field_name)
                .to_tree_node()
                .add_child(_parse_type("_element", type_args[0]))
            )

        case InternalTypes.OPTIONAL:
            return (
                OptionalDeff(field_name=field_name)
                .to_tree_node()
                .add_child(_parse_type("_element", type_args[0]))
            )

        case InternalTypes.OBJECT:
            annotated_fields = get_type_hints(field_type)
            if (
                not annotated_fields
                or not _is_valid_annotation(field_type, annotated_fields)
                or not _is_buildable_class(field_type, annotated_fields)
            ):
                raise TypeError(
                    "The provided type or doesn't have a __annotations__ attribute or doesn't have a compatible __init__ method. "
                    "Ensure that all fields are annotated and that the class can be instantiated with those fields."
                )

            return (
                ObjectDeff(
                    field_name=field_name,
                    field_clzz=field_type,
                    fields=annotated_fields,
                )
                .to_tree_node()
                .extend_children(
                    [
                        _parse_type(sub_field_name, sub_field_type)
                        for sub_field_name, sub_field_type in annotated_fields.items()
                    ]
                )
            )

        case _:
            return FieldsDeff(
                field_name=field_name, field_impl=internal_type.value
            ).to_tree_node()


def struct_parser(obj_or_clzz: T | type[T]) -> TreeNode[StructTyping]:
    clzz = obj_or_clzz if isinstance(obj_or_clzz, type) else type(obj_or_clzz)
    return _parse_type(clzz.__name__, clzz)
