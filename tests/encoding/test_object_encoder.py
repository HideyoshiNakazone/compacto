from compacto.encoding import ObjectEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructTyping, struct_parser

import pytest

from dataclasses import dataclass


class TestListEncoder:
    @pytest.fixture
    def clzz_test(self) -> type:
        @dataclass
        class TestDataclass:
            a: int
            b: str

        return TestDataclass

    @pytest.fixture
    def obj_deff(self, clzz_test: type) -> TreeNode[StructTyping]:
        return struct_parser(clzz_test)

    def test_encode_decode_list_string(
        self, obj_deff: TreeNode[StructTyping], clzz_test: type
    ) -> None:
        test_obj = clzz_test(
            a=42,
            b="hello",
        )

        data = ObjectEncoder.encode(obj_deff, test_obj)
        decoded_obj, _ = ObjectEncoder.decode(obj_deff, data)

        assert test_obj == decoded_obj
