from compacto.encoding.field_encoder import FieldEncoder
from compacto.encoding_headers import OptionFlags
from compacto.struct_parser import FieldsDeff
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

import pytest


SIZE_DOUBLE = InternalTypes.DOUBLE.get_byte_size()


class TestFieldEncoder:
    @pytest.fixture
    def typing_tree(self) -> TreeNode[FieldsDeff]:
        return FieldsDeff("teste", InternalTypes.DOUBLE.value).to_tree_node()

    def test_encode_decode_positive_float(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 3.14, OptionFlags.NONE)
        decoded_value, offset = FieldEncoder._decode(
            typing_tree, data, OptionFlags.NONE
        )

        assert decoded_value == 3.14

    def test_encode_decode_negative_float(self, typing_tree: TreeNode[FieldsDeff]):
        typing_node = FieldsDeff("teste", InternalTypes.DOUBLE.value).to_tree_node()
        data = FieldEncoder._encode(typing_node, -2.718, OptionFlags.NONE)
        decoded_value, offset = FieldEncoder._decode(
            typing_node, data, OptionFlags.NONE
        )

        assert decoded_value == -2.718

    def test_encode_decode_zero(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 0.0, OptionFlags.NONE)
        decoded_value, offset = FieldEncoder._decode(
            typing_tree, data, OptionFlags.NONE
        )

        assert decoded_value == 0.0

    def test_encode_returns_bytes(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 1.0, OptionFlags.NONE)

        assert isinstance(data, bytes)

    def test_decode_offset(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 1.0, OptionFlags.NONE)
        _, offset = FieldEncoder._decode(typing_tree, data, OptionFlags.NONE)

        assert offset == SIZE_DOUBLE
