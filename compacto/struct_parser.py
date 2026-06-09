from compacto.utils.annotations import HasAnnotations
from compacto.utils.constants import Ctype, InternalType, InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import (
    Annotated,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import ctypes
from dataclasses import dataclass
from typing import Iterable, Type


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


@dataclass
class TypeMetadata:
    type: Type
    args: Iterable[Type]
    annotation: Type[ctypes._SimpleCData] | None = None


def _get_origin_type(field_type: type) -> type:
    """Unwrap generic aliases like list[int] → list."""
    return get_origin(field_type) or field_type


def _get_type_metadata(field_type: type) -> TypeMetadata:
    origin = get_origin(field_type) or field_type
    type_args = get_args(field_type)

    if origin is Annotated:
        return TypeMetadata(
            type_args[0],
            (),
            type_args[1],
        )

    return TypeMetadata(origin, type_args)


def _get_validated_annotations(clzz: type) -> dict[str, type]:
    hints = get_type_hints(clzz, include_extras=True)
    if not hints:
        raise TypeError(f"{clzz.__name__} has no annotated fields.")

    # Detect bare class attributes that aren't annotated
    unannotated = {
        k
        for k, v in vars(clzz).items()
        if not k.startswith("__")
        and not callable(v)
        and not isinstance(v, (classmethod, staticmethod, property))
        and k not in hints
    }
    if unannotated:
        raise TypeError(
            f"{clzz.__name__} has unannotated class attributes: {unannotated}. "
            "All fields must be annotated."
        )

    init_params = {k for k in get_type_hints(clzz.__init__) if k != "return"}
    missing = init_params - hints.keys()
    if missing:
        raise TypeError(
            f"{clzz.__name__}.__init__ references unannotated fields: {missing}"
        )

    return hints


def _parse_type(field_name: str, field_type: type) -> TreeNode[StructTyping]:
    type_metadata = _get_type_metadata(field_type)

    internal_type = InternalTypes.get_from_type(
        type_metadata.type, type_metadata.args, ctype=type_metadata.annotation
    )

    match internal_type:
        case InternalTypes.BYTES:
            return BytesDeff(field_name=field_name).to_tree_node()

        case InternalTypes.STRING:
            return StringDeff(field_name=field_name).to_tree_node()

        case InternalTypes.LIST:
            return (
                ListDeff(field_name=field_name)
                .to_tree_node()
                .add_child(_parse_type("_element", type_metadata.args[0]))
            )

        case InternalTypes.OPTIONAL:
            return (
                OptionalDeff(field_name=field_name)
                .to_tree_node()
                .add_child(_parse_type("_element", type_metadata.args[0]))
            )

        case InternalTypes.OBJECT:
            annotated_fields = _get_validated_annotations(field_type)

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
