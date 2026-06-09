from compacto.struct_parser import StructTyping, struct_parser
from compacto.utils.constants import InternalTypes
from compacto.utils.tree_node import TreeNode

from typing_extensions import (
    ClassVar,
    Protocol,
    Self,
    Tuple,
    TypeVar,
    runtime_checkable,
)


T = TypeVar("T")


@runtime_checkable
class TypeEncoder(Protocol):
    mapped_type: ClassVar[InternalTypes]

    __encoders__: dict[InternalTypes, Self] = {}

    @staticmethod
    def encode(node: TreeNode[StructTyping], value: T) -> bytes:
        """
        Encode a value to bytes.
        :param node: definition of the type to encode
        :param value: value to encode
        :return: byte encoded value
        """
        ...

    @staticmethod
    def decode(node: TreeNode[StructTyping], data: bytes) -> Tuple[T, int]:
        """
        Decoder implementation per type
        :param node: definition of the type to decode
        :param data: byte encoded data
        :return: Tuple of (decoded value, number of bytes consumed)
        """
        ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if (mapped_type := getattr(cls, "mapped_type", None)) is None:
            raise TypeError(f"{cls.__name__} must have a 'mapped_type' attribute")

        # if not isinstance(mapped_type, InternalType):
        #     raise TypeError(f"{cls.__name__} must have a 'mapped_type' attribute")

        cls.__encoders__[mapped_type] = cls

    @classmethod
    def get_implementation(cls, type_implementation: InternalTypes) -> Self | None:
        encoder = cls.__encoders__.get(type_implementation, None)
        if encoder is not None:
            return encoder
        return cls.__encoders__.get(InternalTypes.OBJECT, None)

    @classmethod
    def pack(cls, obj: T) -> bytes:
        clzz = type(obj)
        typing_tree = struct_parser(clzz)

        encoder = cls.get_implementation(typing_tree.data.field_type)
        if encoder is None:
            raise TypeError(f"Unsupported field type: {clzz.__name__}")

        return encoder.encode(typing_tree, obj)

    @classmethod
    def unpack(cls, clzz: type[T], data: bytes) -> Tuple[T, int]:
        typing_tree = struct_parser(clzz)

        encoder = cls.get_implementation(typing_tree.data.field_type)
        if encoder is None:
            raise TypeError(f"Unsupported field type: {clzz.__name__}")

        return encoder.decode(typing_tree, data)
