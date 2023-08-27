#! /usr/bin/env python
from src.game.game import Game


HEIGHT = WIDTH = 500
FPS = 60
GAME_DURATION_SEC = 10


if __name__ == "__main__":
    game = Game(HEIGHT, WIDTH, FPS, GAME_DURATION_SEC)
    game.run()
