from __future__ import annotations
from typing import Tuple
import pygame
from pygame import Surface, Vector2

from .direction import Direction

Edge = Tuple[Vector2, Vector2]


class Shape:
    drag_coefficient = 0.0001
    acceleration = 10.0

    def __init__(
        self, screen: Surface, pos: Vector2, radius: float, color: str
    ) -> None:
        self.screen = screen
        self.pos = pos
        self.vel = Vector2(0.0, 0.0)
        self.radius = radius
        self.color = color

    def draw(self) -> None:
        pygame.draw.circle(
            self.screen,
            color=self.color,
            center=self.pos,
            radius=self.radius,
        )

    def accelerate(self, direction: Direction) -> None:
        match direction:
            case Direction.UP:
                self.vel.y -= self.acceleration
            case Direction.DOWN:
                self.vel.y += self.acceleration
            case Direction.LEFT:
                self.vel.x -= self.acceleration
            case Direction.RIGHT:
                self.vel.x += self.acceleration
            case _:
                pass

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        self.add_resistance()

    def add_resistance(self) -> None:
        self.vel -= self.drag_coefficient * self.vel.magnitude() * self.vel

    def overlaps(self, other: Shape) -> bool:
        distance_vec = other.pos - self.pos
        return distance_vec.magnitude() < other.radius + self.radius

    def kick(self, other: Shape) -> None:
        mass = self.radius**2 * 3.14159
        mass_other = other.radius**2 * 3.14159
        vel_diff = self.vel - other.vel
        pos_diff = self.pos - other.pos

        # Equations for 2D elasitc collision
        # https://en.wikipedia.org/wiki/Elastic_collision
        self.vel -= (
            2
            * mass_other
            / (mass + mass_other)
            * vel_diff.dot(pos_diff)
            / pos_diff.magnitude_squared()
            * pos_diff
        )
        other.vel -= (
            2
            * mass
            / (mass + mass_other)
            * -vel_diff.dot(-pos_diff)
            / pos_diff.magnitude_squared()
            * -pos_diff
        )

    def is_colliding_with(self, edge: Edge, on_side: Vector2) -> bool:
        # check vertical:
        point1 = edge[0]
        if self.is_vertical(edge):
            # handle vertical line
            if on_side.x < point1.x:
                # handle right boundary
                return self.pos.x + self.radius >= point1.x
            else:
                # handle left boundary
                return self.pos.x - self.radius <= point1.x

        else:
            # handle horizontal line
            if on_side.y < point1.y:
                # handle bottom boundary
                return self.pos.y + self.radius >= point1.y
            else:
                # handle top boundary
                return self.pos.y - self.radius <= point1.y

    def snap_to(self, edge: Edge, on_side: Vector2) -> None:
        print(f"Snapping to {edge=}")
        if self.is_vertical(edge):
            self.vel.x *= -1
            dx = abs(abs(edge[0].x - self.pos.x) - self.radius)
            if on_side.x < edge[0].x:
                # right boundary
                self.pos.x = edge[0].x - (self.radius + dx)
            else:
                # left boundary
                self.pos.x = edge[0].x + (self.radius + dx)
        else:
            self.vel.y *= -1
            dy = abs(abs(edge[0].y - self.pos.y) - self.radius)
            if on_side.y < edge[0].y:
                # bottom boundary
                self.pos.y = edge[0].y - (self.radius + dy)
            else:
                # top boundary
                self.pos.y = edge[0].y + (self.radius + dy)

    def is_vertical(self, edge: Edge) -> bool:
        edge_span = edge[1] - edge[0]
        return abs(edge_span.y) > abs(edge_span.x)
