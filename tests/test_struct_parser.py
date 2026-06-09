from compacto.struct_parser import (
    FieldsDeff,
    ListDeff,
    ObjectDeff,
    OptionalDeff,
    StringDeff,
    struct_parser,
)

import pytest
from typing_extensions import Optional

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
