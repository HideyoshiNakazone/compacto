from compacto.encoding.field_encoder import FieldEncoder
from compacto.struct_parser import FieldsDeff
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

import pytest


SIZE_DOUBLE = InternalTypes.DOUBLE.get_byte_size(False)


class TestFieldEncoder:
    @pytest.fixture
    def typing_tree(self) -> TreeNode[FieldsDeff]:
        return FieldsDeff("teste", InternalTypes.DOUBLE.value).to_tree_node()

    def test_encode_decode_positive_float(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 3.14)
        decoded_value, offset = FieldEncoder._decode(typing_tree, data)

        assert decoded_value == 3.14

    def test_encode_decode_negative_float(self, typing_tree: TreeNode[FieldsDeff]):
        typing_node = FieldsDeff("teste", InternalTypes.DOUBLE.value).to_tree_node()
        data = FieldEncoder._encode(typing_node, -2.718)
        decoded_value, offset = FieldEncoder._decode(typing_node, data)

        assert decoded_value == -2.718

    def test_encode_decode_zero(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 0.0)
        decoded_value, offset = FieldEncoder._decode(typing_tree, data)

        assert decoded_value == 0.0

    def test_encode_returns_bytes(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 1.0)

        assert isinstance(data, bytes)

    def test_decode_offset(self, typing_tree: TreeNode[FieldsDeff]):
        data = FieldEncoder._encode(typing_tree, 1.0)
        _, offset = FieldEncoder._decode(typing_tree, data)

        assert offset == SIZE_DOUBLE
