from __future__ import annotations
import pygame
from pygame import Vector2
import time

from src.enums.direction import Direction
from src.components.player import Player
from src.components.ball import Ball
from src.components.goals import Goals
from src.components.field import Field


class Game:
    def __init__(
        self, height: int, width: int, fps: int, game_duration_sec: int
    ) -> None:
        self.fps = fps
        self.game_duration_sec = game_duration_sec

        pygame.init()
        pygame.display.set_caption("AFL Simulator")
        self.screen = pygame.display.set_mode((width, height))

        self.setup_field()
        self.place_players_and_ball()

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

    def run(self) -> None:
        self.place_players_and_ball()
        dt = 0.0
        clock = pygame.time.Clock()
        running = True
        start = time.time()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Capture player input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player.accelerate(Direction.UP)
            if keys[pygame.K_s]:
                self.player.accelerate(Direction.DOWN)
            if keys[pygame.K_a]:
                self.player.accelerate(Direction.LEFT)
            if keys[pygame.K_d]:
                self.player.accelerate(Direction.RIGHT)

            # Handle collisions
            self.ball.handle_collision(self.player)
            self.field.resolve_collisions([self.player, self.ball])

            if self.goals.check_goal(self.ball, dt):
                print("Scored a goal!")
                self.place_players_and_ball()

            # Update game state
            self.player.update(dt)
            self.ball.update(dt)

            self.draw()

            dt = clock.tick(self.fps) / 1000

            if time.time() - start >= self.game_duration_sec:
                running = False

        print("GAME OVER")

    def draw(self) -> None:
        self.screen.fill("green")
        self.player.draw()
        self.ball.draw()
        self.goals.draw()
        self.field.draw()
        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
