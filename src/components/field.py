import pygame
from pygame import Vector2, Surface
from typing import List

from ..protocols.snappable import Snappable


class Field:
    def __init__(self, screen: Surface, pos: Vector2, width: float, height: float):
        self.screen = screen
        self.pos = pos
        self.width = width
        self.height = height
        self.corners = [
            Vector2(self.pos.x, self.pos.y),
            Vector2(self.pos.x + self.width, self.pos.y),
            Vector2(self.pos.x + self.width, self.pos.y + self.height),
            Vector2(self.pos.x, self.pos.y + self.height),
        ]
        self.edges = [
            (self.corners[0], self.corners[1]),
            (self.corners[1], self.corners[2]),
            (self.corners[2], self.corners[3]),
            (self.corners[3], self.corners[0]),
        ]

    def draw(self) -> None:
        pygame.draw.lines(self.screen, color="white", closed=True, points=self.corners)

    def resolve_collisions(self, shapes: List[Snappable]) -> None:
        for shape in shapes:
            self.snap_to_colliding_boundary(shape)

    def snap_to_colliding_boundary(self, shape: Snappable) -> None:
        center = Vector2(self.pos.x + self.width / 2, self.pos.y + self.height / 2)
        corners = [
            Vector2(self.pos.x, self.pos.y),
            Vector2(self.pos.x + self.width, self.pos.y),
            Vector2(self.pos.x + self.width, self.pos.y + self.height),
            Vector2(self.pos.x, self.pos.y + self.height),
        ]
        edges = [
            (corners[0], corners[1]),
            (corners[1], corners[2]),
            (corners[2], corners[3]),
            (corners[3], corners[0]),
        ]
        for edge in edges:
            if shape.is_colliding_with(edge, on_side=center):
                shape.snap_to(edge=edge, on_side=center)
