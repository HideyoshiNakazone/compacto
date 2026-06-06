from compacto.encoding import ListEncoder
from compacto.struct_parser import FieldsDeff, ListDeff, StructTyping
from compacto.utils.tree_node import TreeNode

import pytest


class TestListEncoder:
    @pytest.fixture
    def string_list_deff(self) -> TreeNode[StructTyping]:
        return (
            ListDeff("test_list")
            .to_tree_node()
            .add_child(FieldsDeff("test_list", str).to_tree_node())
        )

    @pytest.fixture
    def int_list_deff(self) -> TreeNode[StructTyping]:
        return (
            ListDeff("test_list")
            .to_tree_node()
            .add_child(FieldsDeff("test_list", int).to_tree_node())
        )

    def test_encode_decode_list_string(self, string_list_deff: TreeNode[StructTyping]):
        list_value = [
            "Hello",
            "World",
        ]

        data = ListEncoder.encode(string_list_deff, list_value)
        decoded_list_string, offset = ListEncoder.decode(string_list_deff, data)

        assert list_value == decoded_list_string

    def test_encode_decode_list_int(self, int_list_deff: TreeNode[StructTyping]):
        list_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        data = ListEncoder.encode(int_list_deff, list_value)
        decoded_list_int, offset = ListEncoder.decode(int_list_deff, data)

        assert list_value == decoded_list_int

    def test_encode_decode_empty_list_struct(
        self, int_list_deff: TreeNode[StructTyping]
    ):
        list_value = []

        data = ListEncoder.encode(int_list_deff, list_value)
        decoded_list_int, offset = ListEncoder.decode(int_list_deff, data)

        assert list_value == decoded_list_int
