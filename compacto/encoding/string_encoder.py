from compacto.encoding.type_encoder import TypeEncoder
from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import StructTyping
from compacto.utils.constants import (
    InternalTypes,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import Tuple, Unpack

import struct


class StringEncoder(TypeEncoder):
    mapped_type = InternalTypes.STRING

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping], value: str, **options: Unpack[InternalOptions]
    ) -> bytes:
        encoded = value.encode("utf-8")
        buf = bytearray(InternalTypes.UINT64.get_byte_size() + len(encoded))
        struct.pack_into(InternalTypes.UINT64.get_struct_token(), buf, 0, len(encoded))
        buf[InternalTypes.UINT64.get_byte_size() :] = encoded
        return bytes(buf)

    @staticmethod
    def _decode(
        _: TreeNode[StructTyping], data: bytes, **options: Unpack[InternalOptions]
    ) -> Tuple[str, int]:
        data = memoryview(data)
        (length,) = struct.unpack_from(InternalTypes.UINT64.get_struct_token(), data)
        data = data[InternalTypes.UINT64.get_byte_size() :]
        return data[:length].tobytes().decode(
            "utf-8"
        ), InternalTypes.UINT64.get_byte_size() + length
