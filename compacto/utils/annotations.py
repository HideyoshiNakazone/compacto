from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class HasAnnotations(Protocol):
    __annotations__: dict[str, type]
