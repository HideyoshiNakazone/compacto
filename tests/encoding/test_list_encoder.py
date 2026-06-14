from compacto.encoding import ListEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import FieldsDeff, ListDeff, StringDeff, StructTyping
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

import pytest


class TestListEncoder:
    @pytest.fixture
    def string_list_deff(self) -> TreeNode[StructTyping]:
        return (
            ListDeff("test_list")
            .to_tree_node()
            .add_child(StringDeff("test_list").to_tree_node())
        )

    @pytest.fixture
    def int_list_deff(self) -> TreeNode[StructTyping]:
        return (
            ListDeff("test_list")
            .to_tree_node()
            .add_child(FieldsDeff("test_list", InternalTypes.INT.value).to_tree_node())
        )

    def test_encode_decode_list_string(
        self, string_list_deff: TreeNode[StructTyping], options: InternalOptions
    ):
        list_value = [
            "Hello",
            "World",
        ]

        data = ListEncoder._encode(string_list_deff, list_value, **options)
        decoded_list_string, offset = ListEncoder._decode(
            string_list_deff, data, **options
        )

        assert list_value == decoded_list_string

    def test_encode_decode_list_int(
        self, int_list_deff: TreeNode[StructTyping], options: InternalOptions
    ):
        list_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        data = ListEncoder._encode(int_list_deff, list_value, **options)
        decoded_list_int, offset = ListEncoder._decode(int_list_deff, data, **options)

        assert list_value == decoded_list_int

    def test_encode_decode_empty_list_struct(
        self, int_list_deff: TreeNode[StructTyping], options: InternalOptions
    ):
        list_value = []

        data = ListEncoder._encode(int_list_deff, list_value, **options)
        decoded_list_int, offset = ListEncoder._decode(int_list_deff, data, **options)

        assert list_value == decoded_list_int
