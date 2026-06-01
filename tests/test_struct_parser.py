from compacto.struct_parser import FieldsDeff, StructDeff, struct_parser

import pytest


def test_struct_parser_throws_if_no_annotations() -> None:
    with pytest.raises(TypeError):
        struct_parser({})


def test_struct_parser_throws_if_annotations_are_missing() -> None:
    with pytest.raises(TypeError):

        class NoAnnotations:
            a: str
            b = None

        struct_parser(NoAnnotations)


def test_struct_parser_valid_annotations() -> None:
    class ValidAnnotations:
        a: str
        b: int

    typing_tree = struct_parser(ValidAnnotations)

    assert isinstance(typing_tree.data, StructDeff)
    assert all(isinstance(child.data, FieldsDeff) for child in typing_tree.children)
