from compacto.encoding.optional_encoder import OptionalEncoder
from compacto.struct_parser import (
    FieldsDeff,
    OptionalDeff,
    StringDeff,
    StructTyping,
    struct_parser,
)
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

import pytest
from typing_extensions import Optional

import struct
from dataclasses import dataclass


SIZE_BOOL = InternalTypes.BOOL.get_byte_size()
BOOL_TYPE_TOKEN = InternalTypes.BOOL.get_struct_token()


@dataclass
class _Inner:
    x: int
    y: str


@dataclass
class _OuterOptionalInner:
    field: Optional[_Inner]


class TestOptionalEncoder:
    @pytest.fixture
    def optional_int_node(self) -> TreeNode[StructTyping]:
        return (
            OptionalDeff(field_name="test")
            .to_tree_node()
            .add_child(FieldsDeff("_element", InternalTypes.INT.value).to_tree_node())
        )

    @pytest.fixture
    def optional_str_node(self) -> TreeNode[StructTyping]:
        return (
            OptionalDeff(field_name="test")
            .to_tree_node()
            .add_child(StringDeff("_element").to_tree_node())
        )

    @pytest.fixture
    def optional_obj_node(self) -> TreeNode[StructTyping]:
        outer_tree = struct_parser(_OuterOptionalInner)
        return outer_tree.children[0]

    # --- encode ---

    def test_encode_none_writes_false_flag(
        self, optional_int_node: TreeNode[StructTyping]
    ) -> None:
        data = OptionalEncoder.encode(optional_int_node, None)

        assert len(data) == SIZE_BOOL
        (flag,) = struct.unpack_from(BOOL_TYPE_TOKEN, data)
        assert flag is False

    def test_encode_present_int_writes_true_flag(
        self, optional_int_node: TreeNode[StructTyping]
    ) -> None:
        data = OptionalEncoder.encode(optional_int_node, 42)

        (flag,) = struct.unpack_from(BOOL_TYPE_TOKEN, data)
        assert flag is True
        assert len(data) > SIZE_BOOL

    def test_encode_present_str_writes_true_flag(
        self, optional_str_node: TreeNode[StructTyping]
    ) -> None:
        data = OptionalEncoder.encode(optional_str_node, "hello")

        (flag,) = struct.unpack_from(BOOL_TYPE_TOKEN, data)
        assert flag is True
        assert len(data) > SIZE_BOOL

    # --- decode ---

    def test_decode_none_returns_none_and_flag_offset(
        self, optional_int_node: TreeNode[StructTyping]
    ) -> None:
        none_bytes = struct.pack(BOOL_TYPE_TOKEN, False)

        value, offset = OptionalEncoder.decode(optional_int_node, none_bytes)

        assert value is None
        assert offset == SIZE_BOOL

    # --- roundtrips ---

    def test_roundtrip_none_optional_int(
        self, optional_int_node: TreeNode[StructTyping]
    ) -> None:
        data = OptionalEncoder.encode(optional_int_node, None)
        value, _ = OptionalEncoder.decode(optional_int_node, data)

        assert value is None

    def test_roundtrip_none_optional_str(
        self, optional_str_node: TreeNode[StructTyping]
    ) -> None:
        data = OptionalEncoder.encode(optional_str_node, None)
        value, _ = OptionalEncoder.decode(optional_str_node, data)

        assert value is None

    def test_roundtrip_int(self, optional_int_node: TreeNode[StructTyping]) -> None:
        data = OptionalEncoder.encode(optional_int_node, 42)
        value, _ = OptionalEncoder.decode(optional_int_node, data)

        assert value == 42

    def test_roundtrip_str(self, optional_str_node: TreeNode[StructTyping]) -> None:
        data = OptionalEncoder.encode(optional_str_node, "hello world")
        value, _ = OptionalEncoder.decode(optional_str_node, data)

        assert value == "hello world"

    def test_roundtrip_nested_object(
        self, optional_obj_node: TreeNode[StructTyping]
    ) -> None:
        inner = _Inner(x=10, y="test")

        data = OptionalEncoder.encode(optional_obj_node, inner)
        value, _ = OptionalEncoder.decode(optional_obj_node, data)

        assert value == inner

    def test_roundtrip_none_nested_object(
        self, optional_obj_node: TreeNode[StructTyping]
    ) -> None:
        data = OptionalEncoder.encode(optional_obj_node, None)
        value, _ = OptionalEncoder.decode(optional_obj_node, data)

        assert value is None
