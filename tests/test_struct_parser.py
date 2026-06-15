from compacto.struct_parser import (
    BytesDeff,
    FieldsDeff,
    HashmapDeff,
    ListDeff,
    ObjectDeff,
    OptionalDeff,
    StringDeff,
    struct_parser,
)
from compacto.utils.exceptions import TypeParsingException

import pytest
from typing_extensions import Annotated, Optional, Union

import ctypes
from dataclasses import dataclass


def test_struct_parser_throws_if_no_annotations() -> None:
    with pytest.raises(TypeError):
        _ = struct_parser({})


def test_struct_parser_fallbacks_pickle_if_annotations_are_missing() -> None:
    @dataclass
    class NoAnnotations:
        a: str
        b = None

    with pytest.raises(TypeError):
        _ = struct_parser(NoAnnotations)


def test_struct_parser_valid_annotations() -> None:
    @dataclass
    class ValidAnnotations:
        a: str
        b: int
        c: Optional[int]
        d: list[int]

    typing_tree = struct_parser(ValidAnnotations)

    assert isinstance(typing_tree.data, ObjectDeff)

    assert isinstance(typing_tree.children[0].data, StringDeff)
    assert isinstance(typing_tree.children[1].data, FieldsDeff)
    assert isinstance(typing_tree.children[2].data, OptionalDeff)
    assert isinstance(typing_tree.children[3].data, ListDeff)


def test_struct_parser_bytes_field() -> None:
    @dataclass
    class WithBytes:
        data: bytes

    typing_tree = struct_parser(WithBytes)

    assert isinstance(typing_tree.children[0].data, BytesDeff)


def test_struct_parser_bare_list_raises() -> None:
    @dataclass
    class BareList:
        items: list

    with pytest.raises(
        TypeParsingException, match="list fields must have a type argument"
    ):
        struct_parser(BareList)


def test_struct_parser_union_multiple_non_none_raises() -> None:
    @dataclass
    class MultiUnion:
        x: Union[int, str, None]

    with pytest.raises(
        TypeParsingException, match="optional fields must wrap exactly one type"
    ):
        struct_parser(MultiUnion)


def test_struct_parser_annotated_with_instance_raises() -> None:
    @dataclass
    class BadAnnotation:
        x: Annotated[int, ctypes.c_int32()]  # instance, not a type

    with pytest.raises(TypeParsingException, match="a instance is not accepted"):
        struct_parser(BadAnnotation)


def test_struct_parser_dict() -> None:
    @dataclass
    class WithDict:
        mapping: dict[str, int]

    typing_tree = struct_parser(WithDict)

    assert isinstance(typing_tree.data, ObjectDeff)

    field_tree = typing_tree.children[0]

    assert isinstance(field_tree.data, HashmapDeff)
    assert len(field_tree.children) == 2
