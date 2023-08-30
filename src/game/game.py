from __future__ import annotations
import pygame
from pygame import Vector2, font
from typing import Tuple
import numpy as np
import random

from src.enums.direction import Direction
from src.components.player import Player
from src.components.ball import Ball
from src.components.goals import Goals
from src.components.field import Field
from src.types.actionarr import ActionArr


# reward
# game_iteration


class Game:
    def __init__(
        self, height: int, width: int, fps: int, game_duration_frames: int
    ) -> None:
        self.fps = fps
        self.game_duration_frames = game_duration_frames
        self.height = height
        self.width = width
        self.clock = pygame.time.Clock()

    def reset_game(self) -> None:
        pygame.init()
        self.font = font.SysFont("jetbrainsmononerdfontmono.tff", 48)

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
            Vector2(self.screen.get_width() * 0.4, self.screen.get_height() * 0.15),
            Vector2(self.screen.get_width() * 0.6, self.screen.get_height() * 0.15),
        )
        self.field = Field(
            self.screen,
            Vector2(self.screen.get_width() * 0.1, self.screen.get_height() * 0.1),
            width=self.screen.get_width() * 0.8,
            height=self.screen.get_height() * 0.8,
        )

    def place_players_and_ball(self) -> None:
        ball_start_x = random.uniform(0.15, 0.85)
        ball_start_y = random.uniform(0.15, 0.45)
        ball_start = Vector2(
            self.screen.get_width() * ball_start_x,
            self.screen.get_height() * ball_start_y,
        )

        player_start_x = random.uniform(0.15, 0.85)
        player_start_y = random.uniform(0.55, 0.85)
        player_start = Vector2(
            self.screen.get_width() * player_start_x,
            self.screen.get_height() * player_start_y,
        )

        self.ball.shape.pos = ball_start
        self.ball.shape.vel = Vector2(0, 0)

        self.player.shape.pos = player_start
        self.player.shape.vel = Vector2(0, 0)

    def play_step(self, dt: float, actions: ActionArr) -> Tuple[int, bool, int]:
        reward = 0
        game_over = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # Handle goal score
        if self.goals.check_goal(self.ball, dt):
            self.score += 1
            self.place_players_and_ball()
            reward = 100

        # Handle player input
        actions_list = [
            Direction.RIGHT,
            Direction.DOWN,
            Direction.LEFT,
            Direction.UP,
        ]
        for ix in np.where(actions == 1)[0]:
            self.player.accelerate(actions_list[ix])

        # Handle collisions (with negative rewards)
        reward += self.ball.handle_collision(self.player)
        reward += self.field.resolve_collisions([self.player, self.ball])

        # Update positions
        self.player.update(dt)
        self.ball.update(dt)

        # Pause here to meet target FPS
        # self.clock.tick(self.fps)

        # Draw
        self.draw()

        return reward, game_over, self.score

    def parse_keys(self) -> ActionArr:
        keys = pygame.key.get_pressed()
        watched_keys = [
            pygame.K_d,
            pygame.K_s,
            pygame.K_a,
            pygame.K_w,
        ]

        actions = np.array([int(keys[key]) for key in watched_keys])
        print(actions)

        return actions

    def draw(self) -> None:
        self.screen.fill("green")
        self.player.draw()
        self.ball.draw()
        self.goals.draw()
        self.field.draw()

        WHITE = (255, 255, 255)
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(
            text, (0.001 * self.screen.get_width(), 0.001 * self.screen.get_height())
        )

        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
