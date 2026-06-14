from compacto.encoding_headers import InternalOptions
from compacto.struct_parser import StructTyping
from compacto.utils.constants import InternalType, InternalTypes
from compacto.utils.exceptions import (
    AssertionException,
    DecodingException,
    TypeParsingException,
)
from compacto.utils.tree_node import TreeNode

from typing_extensions import (
    Buffer,
    ClassVar,
    Protocol,
    Self,
    Tuple,
    TypeVar,
    Unpack,
    runtime_checkable,
)


T = TypeVar("T")


@runtime_checkable
class TypeEncoder(Protocol):
    mapped_type: ClassVar[InternalTypes]

    __encoders__: dict[InternalTypes, Self] = {}

    @classmethod
    def encode(
        cls, node: TreeNode[StructTyping], value: T, **options: Unpack[InternalOptions]
    ) -> bytes:
        try:
            return cls._encode(node, value, **options)
        except Exception as err:
            raise DecodingException(
                "Unable to serialize data, likely due to a mismatch between type hinted and the value passed. "
                f"Details: {str(err)}"
            ) from err

    @classmethod
    def decode(
        cls,
        node: TreeNode[StructTyping],
        data: bytes,
        **options: Unpack[InternalOptions],
    ) -> T:
        try:
            data = memoryview(data)
            return cls._decode(node, data, **options)
        except Exception as err:
            raise DecodingException(
                "Unable to deserialize data, likely due to a mismatch between the expected number of bytes "
                f"of the struct definition and the binary data. Details: {str(err)}"
            ) from err

    @staticmethod
    def _encode(
        node: TreeNode[StructTyping], value: T, **options: Unpack[InternalOptions]
    ) -> bytes:
        """
        Encode a value to bytes.
        :param node: definition of the type to encode
        :param value: value to encode
        :return: byte encoded value
        """
        ...

    @staticmethod
    def _decode(
        node: TreeNode[StructTyping], data: Buffer, **options: Unpack[InternalOptions]
    ) -> Tuple[T, int]:
        """
        Decoder implementation per type
        :param node: definition of the type to decode
        :param data: Buffer of encoded data
        :return: Tuple of (decoded value, number of bytes consumed)
        """
        ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if (mapped_type := getattr(cls, "mapped_type", None)) is None:
            raise TypeError(f"{cls.__name__} must have a 'mapped_type' attribute")

        if mapped_type is None or not isinstance(mapped_type.value, InternalType):
            raise AssertionException(
                f"{cls.__name__} must have a 'mapped_type' attribute. This is a Library error, please open an issue :)"
            )

        cls.__encoders__[mapped_type] = cls

    @classmethod
    def get_implementation(cls, type_implementation: InternalTypes) -> Self | None:
        encoder = cls.__encoders__.get(type_implementation, None)
        if encoder is not None:
            return encoder
        return cls.__encoders__.get(InternalTypes.OBJECT, None)

    @classmethod
    def pack(
        cls,
        typing_tree: TreeNode[StructTyping],
        obj: T,
        **options: Unpack[InternalOptions],
    ) -> bytes:
        encoder = cls.get_implementation(typing_tree.data.field_type)
        if encoder is None:
            raise TypeParsingException(f"Unsupported field type: {type(obj).__name__}")

        return encoder.encode(typing_tree, obj, **options)

    @classmethod
    def unpack(
        cls,
        typing_tree: TreeNode[StructTyping],
        data: bytes,
        **options: Unpack[InternalOptions],
    ) -> Tuple[T, int]:
        encoder = cls.get_implementation(typing_tree.data.field_type)
        if encoder is None:
            raise TypeParsingException(
                f"Unsupported field type: {typing_tree.data.field_type.__name__}"
            )

        return encoder.decode(typing_tree, data, **options)
