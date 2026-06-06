from typing_extensions import Protocol


class HasAnnotations(Protocol):
    __annotations__: dict[str, type]
