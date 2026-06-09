from compacto.struct_parser import FieldsDeff, StructTyping
from compacto.utils.tree_node import TreeNode

from typing_extensions import Self

import hashlib
import struct
from dataclasses import dataclass


ENCODING_HASH_SIZE = 4

VERSION_ENCODING_TOKEN = ">H"
SIZE_OF_VERSION_BYTES = struct.calcsize(VERSION_ENCODING_TOKEN)


def calc_hash_from_tree(typing_tree: TreeNode[StructTyping]) -> bytes:
    h = hashlib.blake2b(digest_size=ENCODING_HASH_SIZE)

    deff = typing_tree.data
    h.update(type(deff).__name__.encode())
    h.update(deff.field_name.encode())

    if isinstance(deff, FieldsDeff):
        h.update(deff.field_impl.ctype.__name__.encode())

    for child in typing_tree.children:
        h.update(calc_hash_from_tree(child))

    return h.digest()


@dataclass
class EncodingHeader:
    version: int
    schema_hash: bytes

    def encode(self) -> bytearray:
        data = bytearray()
        data.extend(struct.pack(VERSION_ENCODING_TOKEN, self.version))
        data.extend(self.schema_hash)  # raw bytes, no struct.pack
        return data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        version = struct.unpack(VERSION_ENCODING_TOKEN, data[:SIZE_OF_VERSION_BYTES])[0]
        type_hash = data[
            SIZE_OF_VERSION_BYTES : SIZE_OF_VERSION_BYTES + ENCODING_HASH_SIZE
        ]
        return cls(version, type_hash)

    @classmethod
    def from_params(cls, version: int, typing_tree: TreeNode[StructTyping]) -> Self:
        type_hash = calc_hash_from_tree(typing_tree)
        return cls(version, type_hash)

    @property
    def size_of_header(self) -> int:
        return SIZE_OF_VERSION_BYTES + ENCODING_HASH_SIZE  # version + sha256
