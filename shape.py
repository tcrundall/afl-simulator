from __future__ import annotations
import pygame
from pygame import Surface, Vector2

from direction import Direction


class Shape():
    drag_coefficient = 0.001
    acceleration = 10.

    def __init__(
            self, screen: Surface, pos: Vector2, radius: float, color: str
        ) -> None:

        self.screen = screen
        self.pos = pos
        self.vel = Vector2(0., 0.)
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

    def add_resistance(self):
        self.vel -= self.drag_coefficient * self.vel.magnitude() * self.vel

    def overlaps(self, other: Shape):
        distance_vec = other.pos - self.pos
        return distance_vec.magnitude() < other.radius + self.radius

    def kick(self, other: Shape):
        mass = self.radius ** 2 * 3.14159
        mass_other = other.radius ** 2 * 3.14159
        vel_diff = self.vel - other.vel
        pos_diff = self.pos - other.pos

        # Equations for 2D elasitc collision
        # https://en.wikipedia.org/wiki/Elastic_collision
        self.vel -=\
            2 * mass_other / (mass + mass_other)\
            * vel_diff.dot(pos_diff) / pos_diff.magnitude_squared()\
            * pos_diff
        other.vel -=\
            2 * mass / (mass + mass_other)\
            * -vel_diff.dot(-pos_diff) / pos_diff.magnitude_squared()\
            * -pos_diff
