from typing_extensions import Generic, Iterator, Self, TypeVar

from dataclasses import dataclass


V = TypeVar("V")


@dataclass
class TreeNode(Generic[V]):
    parent: Self | None
    children: list[Self]
    data: V

    @classmethod
    def new(cls, data: V, parent: Self | None = None) -> Self:
        return cls(parent=parent, children=[], data=data)

    def add_child(self, child: Self) -> Self:
        child.parent = self
        self.children.append(child)
        return self

    def extend_children(self, children: list[Self]) -> Self:
        for child in children:
            child.parent = self
        self.children.extend(children)
        return self

    def __iter__(self) -> Iterator[Self]:
        for child in self.children:
            yield child
