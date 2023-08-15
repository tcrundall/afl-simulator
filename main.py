#! /usr/bin/env python
from __future__ import annotations
import pygame
from pygame import Vector2
import time

from direction import Direction
from agent import Agent
from ball import Ball
from goals import Goals


HEIGHT = WIDTH = 500
FPS = 60


def main() -> None:
    pygame.init()
    pygame.display.set_caption("AFL Simulator")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    ball_start = Vector2(screen.get_width()*0.5, screen.get_height()*0.4)
    agent_start = Vector2(screen.get_width()*0.5, screen.get_height()*0.2)

    agent = Agent(screen, agent_start.copy())
    ball = Ball(screen, ball_start.copy())
    goals = Goals(
        screen,
        Vector2(screen.get_width()*0.25, screen.get_height()*0.5),
        Vector2(screen.get_width()*0.75, screen.get_height()*0.5),
    )

    after_goal_frames = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("green")
        agent.draw()
        ball.draw()
        goals.draw()

        # Capture player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            agent.accelerate(Direction.UP)
        if keys[pygame.K_s]:
            agent.accelerate(Direction.DOWN)
        if keys[pygame.K_a]:
            agent.accelerate(Direction.LEFT)
        if keys[pygame.K_d]:
            agent.accelerate(Direction.RIGHT)

        # Handle collisions
        ball.handle_collision(agent)

        if goals.check_goal(ball, dt):
            print("Scored a goal!")
            ball.shape.pos = ball_start.copy()
            ball.shape.vel = Vector2(0, 0)
            agent.shape.pos = agent_start.copy()
            agent.shape.vel = Vector2(0, 0)
            after_goal_frames = None

        # Update game state
        agent.update(dt)
        ball.update(dt)

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000
        if after_goal_frames is not None:
            after_goal_frames -= 1


if __name__ == "__main__":
    main()
