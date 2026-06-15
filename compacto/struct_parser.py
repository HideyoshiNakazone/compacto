from compacto.utils.annotations import HasAnnotations
from compacto.utils.constants import Ctype, InternalType, InternalTypes
from compacto.utils.exceptions import TypeParsingException
from compacto.utils.tree_node import TreeNode

from typing_extensions import (
    Annotated,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import ctypes
from dataclasses import dataclass


T = TypeVar("T", bound=HasAnnotations)


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


@dataclass
class HashmapDeff(_GenericTypeDeff):
    field_name: str
    field_type = InternalTypes.HASHMAP


StructTyping = Union[
    BytesDeff, StringDeff, ListDeff, OptionalDeff, ObjectDeff, FieldsDeff, HashmapDeff
]


@dataclass
class TypeMetadata:
    type: Type
    args: tuple[Type, ...]
    annotation: Type[ctypes._SimpleCData] | None = None


def _unwrap_annotated(
    field_type: type,
) -> tuple[type, Type[ctypes._SimpleCData] | None]:
    if get_origin(field_type) is Annotated:
        args = get_args(field_type)

        if not (isinstance(args[1], type) and issubclass(args[1], ctypes._SimpleCData)):
            raise TypeParsingException(
                "Only type ctypes are permited as annotations, a instance is not accepted, "
                "e.g. Annotated[int, ctypes.c_int32] is valid, but Annotated[int, ctypes.c_int32()] is not."
            )

        return args[0], args[1]

    return field_type, None


def _get_type_metadata(field_type: type) -> TypeMetadata:
    inner, annotation = _unwrap_annotated(field_type)
    return TypeMetadata(
        type=get_origin(inner) or inner,
        args=get_args(inner),
        annotation=annotation,
    )


def _get_validated_annotations(clzz: type) -> dict[str, type]:
    hints = get_type_hints(clzz, include_extras=True)
    if not hints:
        raise TypeParsingException(f"{clzz.__name__} has no annotated fields.")

    # Detect bare class attributes that aren't annotated
    unannotated = {
        k
        for k, v in vars(clzz).items()
        if not k.startswith("_")
        and not callable(v)
        and not isinstance(v, (classmethod, staticmethod, property))
        and k not in hints
        and k != "model_config"  # added for pydantic compatibility
    }
    if unannotated:
        raise TypeParsingException(
            f"{clzz.__name__} has unannotated class attributes: {unannotated}. "
            "All fields must be annotated."
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
            if not type_metadata.args:
                raise TypeParsingException(
                    "list fields must have a type argument, e.g. list[int]"
                )
            return (
                ListDeff(field_name=field_name)
                .to_tree_node()
                .add_child(_parse_type("_element", type_metadata.args[0]))
            )

        case InternalTypes.OPTIONAL:
            if not type_metadata.args:
                raise TypeParsingException(
                    "optional fields must have a type argument, e.g. Optional[int] or int | None"
                )
            inner_args = [a for a in type_metadata.args if a is not type(None)]
            if len(inner_args) != 1:
                raise TypeParsingException(
                    "optional fields must wrap exactly one type, e.g. Optional[int]"
                )
            return (
                OptionalDeff(field_name=field_name)
                .to_tree_node()
                .add_child(_parse_type("_element", inner_args[0]))
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

        case InternalTypes.HASHMAP:
            if len(type_metadata.args) != 2:
                raise TypeParsingException(
                    "hashmap requires typing for both key and value types, e.g. dict[str, int]"
                )

            return (
                HashmapDeff(
                    field_name=field_name,
                )
                .to_tree_node()
                .extend_children(
                    [
                        _parse_type("_key", type_metadata.args[0]),
                        _parse_type("_value", type_metadata.args[1]),
                    ]
                )
            )

        case _ if isinstance(internal_type.value, Ctype):
            return FieldsDeff(
                field_name=field_name, field_impl=internal_type.value
            ).to_tree_node()

        case _:
            raise TypeParsingException(
                f"No parser defined for internal type: {internal_type}"
            )


def struct_parser(obj_or_clzz: T | type[T]) -> TreeNode[StructTyping]:
    clzz = obj_or_clzz if isinstance(obj_or_clzz, type) else type(obj_or_clzz)
    return _parse_type(clzz.__name__, clzz)
