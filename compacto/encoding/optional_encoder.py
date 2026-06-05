from compacto.encoding import TypeEncoder
from compacto.internal_types import TreeNode
from compacto.struct_parser import StructTyping

from typing import Optional, Tuple


class OptionalEncoder(TypeEncoder[Optional]):
    @staticmethod
    def encode(node: TreeNode[StructTyping], value: Optional) -> bytes: ...

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[Optional, int]: ...
