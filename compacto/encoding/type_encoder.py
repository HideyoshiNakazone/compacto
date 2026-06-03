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
class TypeEncoder(Protocol[T]):
    mapped_type: ClassVar[type]

    __encoders__: dict[type, Self] = {}

    @staticmethod
    def encode(value: T) -> bytes:
        """
        Encode a value to bytes.
        :param value: value to encode
        :return: byte encoded value
        """
        ...

    @staticmethod
    def decode(data: bytes) -> Tuple[T, int]:
        """
        Decoder implementation per type
        :param data: byte encoded data
        :return: Tuple of (decoded value, number of bytes consumed)
        """
        ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if (mapped_type := getattr(cls, "mapped_type", None)) is None:
            raise TypeError(f"{cls.__name__} must have a 'mapped_type' attribute")
        cls.__encoders__[mapped_type] = cls

    @classmethod
    def get_implementation(cls, type_: type) -> Self:
        if encoder := cls.__encoders__.get(type_, None):
            return encoder
        raise TypeError(f"No encoder found for type {type_.__name__}")
