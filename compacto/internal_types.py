from dataclasses import dataclass
from typing import Generic, Iterator, Protocol, Self, TypeVar


class HasAnnotations(Protocol):
    __annotations__: dict[str, type]


V = TypeVar("V")


@dataclass
class TreeNode(Generic[V]):
    parent: Self | None
    children: list[Self]
    data: V

    @classmethod
    def new(cls, data: V, parent: Self | None = None) -> Self:
        return cls(parent=parent, children=[], data=data)

    def add_child(self, child: Self) -> None:
        child.parent = self
        self.children.append(child)

    def __iter__(self) -> Iterator[V]:
        yield self.data
        for child in self.children:
            yield from child
