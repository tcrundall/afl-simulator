from typing import Protocol, Tuple
from pygame import Vector2

Edge = Tuple[Vector2, Vector2]


class Snappable(Protocol):
    def draw(self) -> None:
        ...

    def is_colliding_with(self, edge: Edge, on_side: Vector2) -> bool:
        ...

    def snap_to(self, edge: Edge, on_side: Vector2) -> None:
        ...
