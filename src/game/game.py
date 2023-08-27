from __future__ import annotations
import pygame
from pygame import Vector2
import time
from typing import Tuple, List

from src.enums.direction import Direction
from src.components.player import Player
from src.components.ball import Ball
from src.components.goals import Goals
from src.components.field import Field


# reward
# game_iteration


class Game:
    def __init__(
        self, height: int, width: int, fps: int, game_duration_sec: int
    ) -> None:
        self.fps = fps
        self.game_duration_sec = game_duration_sec
        self.height = height
        self.width = width

    def reset_game(self) -> None:
        pygame.init()
        pygame.display.set_caption("AFL Simulator")
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.setup_field()
        self.place_players_and_ball()

        self.score = 0

    def setup_field(self) -> None:
        self.player = Player(self.screen, Vector2(-100, -100))
        self.ball = Ball(self.screen, Vector2(-100, -200))
        self.goals = Goals(
            self.screen,
            Vector2(self.screen.get_width() * 0.25, self.screen.get_height() * 0.5),
            Vector2(self.screen.get_width() * 0.75, self.screen.get_height() * 0.5),
        )
        self.field = Field(
            self.screen,
            Vector2(self.screen.get_width() * 0.1, self.screen.get_height() * 0.1),
            width=self.screen.get_width() * 0.8,
            height=self.screen.get_height() * 0.8,
        )

    def place_players_and_ball(self) -> None:
        ball_start = Vector2(
            self.screen.get_width() * 0.5, self.screen.get_height() * 0.4
        )
        player_start = Vector2(
            self.screen.get_width() * 0.5, self.screen.get_height() * 0.2
        )

        self.ball.shape.pos = ball_start
        self.ball.shape.vel = Vector2(0, 0)

        self.player.shape.pos = player_start
        self.player.shape.vel = Vector2(0, 0)

    def play_step(self, dt: float, actions: List[Direction]) -> Tuple[bool, int]:
        game_over = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # Handle goal score
        if self.goals.check_goal(self.ball, dt):
            self.score += 1
            self.place_players_and_ball()

        # Handle player input
        for direction in actions:
            self.player.accelerate(direction)

        # Handle collisions
        self.ball.handle_collision(self.player)
        self.field.resolve_collisions([self.player, self.ball])

        # Update positions
        self.player.update(dt)
        self.ball.update(dt)

        # Draw
        self.draw()

        return game_over, self.score

    def parse_keys(self) -> List[Direction]:
        keys = pygame.key.get_pressed()

        actions = []
        if keys[pygame.K_w]:
            actions.append(Direction.UP)
        if keys[pygame.K_s]:
            actions.append(Direction.DOWN)
        if keys[pygame.K_a]:
            actions.append(Direction.LEFT)
        if keys[pygame.K_d]:
            actions.append(Direction.RIGHT)

        return actions

    def run(self) -> None:
        dt = 0.0
        clock = pygame.time.Clock()
        running = True
        start = time.time()

        while running:
            self.play_step(dt, actions=self.parse_keys())
            dt = clock.tick(self.fps) / 1000
            if time.time() - start >= self.game_duration_sec:
                running = False

        pygame.quit()

    def draw(self) -> None:
        self.screen.fill("green")
        self.player.draw()
        self.ball.draw()
        self.goals.draw()
        self.field.draw()
        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
