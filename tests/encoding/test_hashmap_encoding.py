from compacto.encoding.hashmap_encoder import HashmapEncoder
from compacto.struct_parser import HashmapDeff, StringDeff, struct_parser
from compacto.utils.tree_node import TreeNode

import pytest

from dataclasses import dataclass


class TestHashmapEncoding:
    def test_encoder_decoder_with_dict_str_int(self) -> None:
        obj_deff = struct_parser(dict[str, int])

        test_obj = {
            "a": 1,
            "b": 2,
            "c": 3,
        }

        data = HashmapEncoder.encode(obj_deff, test_obj)
        decoded_obj, offset = HashmapEncoder.decode(obj_deff, data)

        assert test_obj == decoded_obj

    def test_encoder_decoder_with_dict_str_clzz(self) -> None:
        @dataclass
        class DataWrapper:
            a: int

        obj_deff = struct_parser(dict[str, DataWrapper])

        test_obj = {
            "a": DataWrapper(1),
            "b": DataWrapper(2),
            "c": DataWrapper(3),
        }

        data = HashmapEncoder.encode(obj_deff, test_obj)
        decoded_obj, offset = HashmapEncoder.decode(obj_deff, data)

        assert test_obj == decoded_obj

    def test_encode_raises_when_node_data_is_not_hashmap_deff(self) -> None:
        node = TreeNode.new(StringDeff(field_name="test"))

        with pytest.raises(TypeError, match="Unsupported field type"):
            HashmapEncoder._encode(node, {})

    def test_encode_raises_when_children_count_is_zero(self) -> None:
        node = TreeNode.new(HashmapDeff(field_name="test"))

        with pytest.raises(TypeError, match="Expected exactly 2 child fields"):
            HashmapEncoder._encode(node, {})

    def test_encode_raises_when_children_count_is_one(self) -> None:
        node = TreeNode.new(HashmapDeff(field_name="test"))
        node.add_child(TreeNode.new(StringDeff(field_name="_key")))

        with pytest.raises(TypeError, match="Expected exactly 2 child fields"):
            HashmapEncoder._encode(node, {})

    def test_encode_raises_when_children_count_is_three(self) -> None:
        node = TreeNode.new(HashmapDeff(field_name="test"))
        for name in ("_key", "_value", "_extra"):
            node.add_child(TreeNode.new(StringDeff(field_name=name)))

        with pytest.raises(TypeError, match="Expected exactly 2 child fields"):
            HashmapEncoder._encode(node, {})

    def test_decode_raises_when_node_data_is_not_hashmap_deff(self) -> None:
        node = TreeNode.new(StringDeff(field_name="test"))

        with pytest.raises(TypeError, match="Unsupported field type"):
            HashmapEncoder._decode(node, b"\x00" * 4)

    def test_decode_raises_when_children_count_is_zero(self) -> None:
        node = TreeNode.new(HashmapDeff(field_name="test"))

        with pytest.raises(TypeError, match="Expected exactly 2 child fields"):
            HashmapEncoder._decode(node, b"\x00" * 4)

    def test_decode_raises_when_children_count_is_one(self) -> None:
        node = TreeNode.new(HashmapDeff(field_name="test"))
        node.add_child(TreeNode.new(StringDeff(field_name="_key")))

        with pytest.raises(TypeError, match="Expected exactly 2 child fields"):
            HashmapEncoder._decode(node, b"\x00" * 4)

    def test_decode_raises_when_children_count_is_three(self) -> None:
        node = TreeNode.new(HashmapDeff(field_name="test"))
        for name in ("_key", "_value", "_extra"):
            node.add_child(TreeNode.new(StringDeff(field_name=name)))

        with pytest.raises(TypeError, match="Expected exactly 2 child fields"):
            HashmapEncoder._decode(node, b"\x00" * 4)
