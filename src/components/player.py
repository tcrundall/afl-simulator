from typing import Tuple
from pygame import Surface, Vector2

from ..enums.direction import Direction
from .shape import Shape


Edge = Tuple[Vector2, Vector2]


class Player:
    color = "blue"
    radius = 10.0

    def __init__(self, screen: Surface, pos: Vector2) -> None:
        self.shape = Shape(screen, pos, self.radius, self.color)

    def accelerate(self, direction: Direction) -> None:
        self.shape.accelerate(direction)

    def draw(self) -> None:
        self.shape.draw()

    def update(self, dt: float) -> None:
        self.shape.update(dt)

    def is_colliding_with(self, edge: Edge, on_side: Vector2) -> bool:
        return self.shape.is_colliding_with(edge, on_side)

    def snap_to(self, edge: Edge, on_side: Vector2) -> None:
        self.shape.snap_to(edge, on_side)
