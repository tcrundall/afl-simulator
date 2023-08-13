#! /usr/bin/env python
from __future__ import annotations
import pygame
from pygame import Vector2
import time

from direction import Direction
from agent import Agent
from ball import Ball


HEIGHT = WIDTH = 500


class Goals:
    post_radius = 5.

    def __init__(self, screen, left_pos: Vector2, right_pos: Vector2):
        self.screen = screen
        self.left_pos = left_pos
        self.right_pos = right_pos

    def draw(self):
        pygame.draw.circle(
            self.screen,
            color="white",
            center=self.left_pos,
            radius=self.post_radius
        )
        pygame.draw.circle(
            self.screen,
            color="white",
            center=self.right_pos,
            radius=self.post_radius
        )
        post_diff = self.right_pos - self.left_pos
        pygame.draw.line(self.screen, "black", self.left_pos, self.left_pos + post_diff)

    def check_goal(self, ball: Ball, dt: float):
        # Check if path taken by ball intersects goal line
        # Using cross product solution provided by
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        # @gareth-rees
        
        if ball.shape.vel.magnitude() == 0.:
            return

        post_diff = self.right_pos - self.left_pos
        ball_pos_old = ball.shape.pos - ball.shape.vel * dt
        ball_trail = - ball.shape.pos + ball_pos_old

        try:
            t = (ball.shape.pos - self.left_pos).cross(ball_trail)\
                / (post_diff.cross(ball_trail))

            u = (ball.shape.pos - self.left_pos).cross(post_diff)\
                / (post_diff.cross(ball_trail))
            
            pygame.draw.line(self.screen, "black", ball.shape.pos, ball_pos_old)
            if (0 <= t <= 1 and 0 <= u <= 1):
                return True

        except ZeroDivisionError:
            return


def main() -> None:
    pygame.init()
    pygame.display.set_caption("AFL Simulator")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    ball_start = Vector2(screen.get_width()/2, screen.get_height()*0.2)
    agent_start = Vector2(screen.get_width()*0.5, screen.get_height()*0.3)

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

        dt = clock.tick(10) / 1000
        if after_goal_frames is not None:
            after_goal_frames -= 1


if __name__ == "__main__":
    main()
