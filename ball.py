from pygame import Surface, Vector2

from direction import Direction
from shape import Shape
from agent import Agent


class Ball():
    color = "red"
    radius = 2.

    def __init__(self, screen: Surface, pos: Vector2) -> None:
        self.shape = Shape(screen, pos, self.radius, self.color)

    def accelerate(self, direction: Direction) -> None:
        self.shape.accelerate(direction)

    def draw(self) -> None:
        self.shape.draw()

    def update(self, dt: float) -> None:
        self.shape.update(dt)

    def handle_collision(self, agent: Agent):
        if not self.shape.overlaps(agent.shape):
            return

        print("Overlapping!!")
        self.shape.kick(agent.shape)