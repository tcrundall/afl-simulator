#! /usr/bin/env python
from __future__ import annotations
import pygame
from pygame import Vector2

from src.enums.direction import Direction
from src.components.player import Player
from src.components.ball import Ball
from src.components.goals import Goals
from src.components.field import Field


HEIGHT = WIDTH = 500
FPS = 60


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
