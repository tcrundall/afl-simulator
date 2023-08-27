import pygame
import time

from src.game.game import Game
from src.enums.direction import Direction


class Agent:
    def __init__(self, game: Game) -> None:
        self.game = game

    def play_game(self) -> None:
        self.game.reset_game()
        dt = 0.0
        clock = pygame.time.Clock()
        running = True
        start = time.time()

        while running:
            self.game.play_step(dt, actions=self.model())
            dt = clock.tick(self.game.fps) / 1000
            if time.time() - start >= self.game.game_duration_sec:
                running = False

        pygame.quit()

    def play_game_many_times(self, n_replays: int) -> None:
        for _ in range(n_replays):
            self.game.reset_game()
            # self.game.run()

    def model(self):
        return [Direction.LEFT]
