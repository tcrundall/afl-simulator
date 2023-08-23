#! /usr/bin/env python
from __future__ import annotations
from typing import List
import pygame
from pygame import Vector2, Surface

from .protocols.snappable import Snappable
from .direction import Direction
from .player import Player
from .ball import Ball
from .goals import Goals


HEIGHT = WIDTH = 500
FPS = 60


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


def main() -> None:
    pygame.init()
    pygame.display.set_caption("AFL Simulator")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    dt = 0.0
    ball_start = Vector2(screen.get_width() * 0.5, screen.get_height() * 0.4)
    player_start = Vector2(screen.get_width() * 0.5, screen.get_height() * 0.2)

    player = Player(screen, player_start.copy())
    ball = Ball(screen, ball_start.copy())
    goals = Goals(
        screen,
        Vector2(screen.get_width() * 0.25, screen.get_height() * 0.5),
        Vector2(screen.get_width() * 0.75, screen.get_height() * 0.5),
    )
    field = Field(
        screen,
        Vector2(screen.get_width() * 0.1, screen.get_height() * 0.1),
        width=screen.get_width() * 0.8,
        height=screen.get_height() * 0.8,
    )

    after_goal_frames = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("green")
        player.draw()
        ball.draw()
        goals.draw()
        field.draw()

        # Capture player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.accelerate(Direction.UP)
        if keys[pygame.K_s]:
            player.accelerate(Direction.DOWN)
        if keys[pygame.K_a]:
            player.accelerate(Direction.LEFT)
        if keys[pygame.K_d]:
            player.accelerate(Direction.RIGHT)

        # Handle collisions
        ball.handle_collision(player)
        field.resolve_collisions([player, ball])

        if goals.check_goal(ball, dt):
            print("Scored a goal!")
            ball.shape.pos = ball_start.copy()
            ball.shape.vel = Vector2(0, 0)
            player.shape.pos = player_start.copy()
            player.shape.vel = Vector2(0, 0)
            after_goal_frames = None

        # Update game state
        player.update(dt)
        ball.update(dt)

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000
        if after_goal_frames is not None:
            after_goal_frames -= 1


if __name__ == "__main__":
    main()
