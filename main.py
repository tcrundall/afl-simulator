#! /usr/bin/env python
from src.game.game import Game
from src.agent.agent import Agent


HEIGHT = WIDTH = 500
FPS = 60
GAME_DURATION_SEC = 5


if __name__ == "__main__":
    game = Game(HEIGHT, WIDTH, FPS, GAME_DURATION_SEC)
    agent = Agent(game)
    agent.play_game_many_times(1)
