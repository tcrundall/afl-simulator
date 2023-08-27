import pygame
import time
from typing import Dict
import numpy as np

from src.game.game import Game
from src.types.actionarr import ActionArr


class Agent:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.scores: Dict[str, int] = {}

    def play_game(self, agent_id: str) -> None:
        self.game.reset_game()
        dt = 0.0
        score = 0
        clock = pygame.time.Clock()
        running = True
        start = time.time()

        while running:
            _, game_over, score = self.game.play_step(dt, actions=self.model())
            dt = clock.tick(self.game.fps) / 1000
            if game_over or (time.time() - start >= self.game.game_duration_sec):
                running = False

        pygame.quit()
        self.scores[agent_id] = score
        print(f"Agent {agent_id} got score {score}")

    def model(self) -> ActionArr:
        return np.array([0, 1, 0, 0])

    def play_agent(self, count: int) -> None:
        for agent_id in range(count):
            self.play_game(str(agent_id))
