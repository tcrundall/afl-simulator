import torch
import random
import pygame
import time
import numpy as np
from collections import deque

from src.game.game import Game
from src.types.actionarr import ActionArr, StateArr

MAX_MEMORY = 100_000
BATCH_SIZE = 1_000
LR = 0.001


class Agent:
    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0.0  # randomness
        self.gamma = 0.0  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = None  # TODO
        self.trainer = None  # TODO

    def get_state(self, game: Game) -> StateArr:
        state = [
            game.player.shape.pos.x,
            game.player.shape.pos.y,
            game.player.shape.vel.x,
            game.player.shape.vel.y,
            game.ball.shape.pos.x,
            game.ball.shape.pos.y,
            game.ball.shape.vel.x,
            game.ball.shape.vel.y,
            game.goals.left_pos.x,
            game.goals.left_pos.y,
            game.goals.right_pos.x,
            game.goals.right_pos.y,
        ]
        return np.array(state)

    def remember(
        self,
        state: StateArr,
        action: ActionArr,
        reward: int,
        next_state: StateArr,
        game_over: bool,
    ):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(
        self,
        state: StateArr,
        action: ActionArr,
        reward: int,
        next_state: StateArr,
        game_over: bool,
    ) -> None:
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state) -> ActionArr:
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 3)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state0)
            move = int(torch.argmax(prediction).item())

        final_move[move] = 1
        return np.array(final_move)

    def play_game(self, game: Game, agent_id: str) -> None:
        game.reset_game()
        score = 0
        clock = pygame.time.Clock()
        running = True
        start = time.time()
        DT = game.fps / 1000  # Don't want training influenced by frame-rate

        while running:
            _, game_over, score = game.play_step(
                DT, actions=self.get_action(self.get_state(game))
            )
            clock.tick(game.fps)
            if game_over or (time.time() - start >= game.game_duration_sec):
                running = False

        pygame.quit()
        print(f"Agent {agent_id} got score {score}")


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Game(width=50, height=50, fps=60, game_duration_sec=10)
    dt = 1 / 60.0 / 1000.0
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, game_over, score = game.play_step(dt, final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        # remmeber
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory
            game.reset_game()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # TODO: agent.model.save()

            print(f"Game {agent.n_games}, Score {score}, Record: {record}")
            # TODO: plot


if __name__ == "__main__":
    train()
