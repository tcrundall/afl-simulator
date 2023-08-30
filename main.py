#! /usr/bin/env python
import sys

from src.agent.agent import train, play, play_human


HEIGHT = WIDTH = 400
FPS = 60
GAME_DURATION_FRAMES = 1500


if __name__ == "__main__":
    if sys.argv[1] == "train":
        train(WIDTH, HEIGHT, FPS, GAME_DURATION_FRAMES)
    elif sys.argv[1] == "human":
        play_human(WIDTH, HEIGHT, FPS, 1_000_000_000)
    else:
        play(WIDTH, HEIGHT, FPS, GAME_DURATION_FRAMES)
