from compacto.struct_parser import FieldsDeff, StructDeff, struct_parser

import pytest

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

    typing_tree = struct_parser(ValidAnnotations)

    assert isinstance(typing_tree.data, StructDeff)
    assert all(isinstance(child.data, FieldsDeff) for child in typing_tree.children)
