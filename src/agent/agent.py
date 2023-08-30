import torch
import random
import pygame
import time
import numpy as np
from collections import deque
from typing import Any, Tuple, Deque, List
import os

from src.game.game import Game
from src.types.actionarr import ActionArr, StateArr
from src.model.model import Linear_QNet, QTrainer
from src.visuals.plot import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1_000
STATE_SIZE = 12
HIDDEN1_SIZE = 32
HIDDEN2_SIZE = 32
HIDDEN3_SIZE = 32
ACTION_SIZE = 4
LR = 0.001

Memory = Tuple[
    StateArr,
    ActionArr,
    int,
    StateArr,
    bool,
]


class Agent:
    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0.0  # randomness
        self.gamma = 0.9  # discount rate, < 1
        self.memory: Deque[Any] = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(
            input_size=STATE_SIZE,
            hidden1_size=HIDDEN1_SIZE,
            hidden2_size=HIDDEN2_SIZE,
            hidden3_size=HIDDEN3_SIZE,
            output_size=ACTION_SIZE,
        )
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

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
    ) -> None:
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self) -> None:
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = list(self.memory)

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
        self.trainer.train_single_step(state, action, reward, next_state, game_over)

    def get_action(self, state: StateArr) -> ActionArr:
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0]
        # if random.randint(0, 200) < self.epsilon:
        #     move = random.randint(0, 3)
        # else:
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
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
            if game_over or (time.time() - start >= game.game_duration_frames):
                running = False

        pygame.quit()
        print(f"Agent {agent_id} got score {score}")

    def save_checkpoint(
        self, checkpoint_name: str, scores: List[int], mean_scores: List[float]
    ) -> None:
        checkpoint = {
            "model": self.model.state_dict(),
            "optimizer": self.trainer.optimizer.state_dict(),
            "memory": self.memory,
            "scores": scores,
            "mean_scores": mean_scores,
        }
        file_path = f"./checkpoints/{checkpoint_name}.tar"
        if not os.path.isfile(file_path):
            torch.save(checkpoint, f"./checkpoints/{checkpoint_name}.tar")

    def load_checkpoint(
        self, full_checkpoint_filepath: str, train: bool = False
    ) -> Tuple[List[int], List[float]]:
        checkpoint = torch.load(full_checkpoint_filepath)
        self.model.load_state_dict(checkpoint["model"])
        self.trainer.optimizer.load_state_dict(checkpoint["optimizer"])

        if train:
            self.model.train()
            self.memory = checkpoint["memory"]
        else:
            self.model.eval()

        return checkpoint["scores"], checkpoint["mean_scores"]


def train(width: int, height: int, fps: int, game_duration_frames: int) -> None:
    print("Setting up training...")
    plot_scores: List[int] = []
    plot_mean_scores: List[float] = []
    total_score = 0
    record = 0
    skip_next_checkpoint_save = False
    agent = Agent()

    checkpoint_filename = get_latest_checkpoint_filename()
    if checkpoint_filename:
        plot_scores, plot_mean_scores = agent.load_checkpoint(checkpoint_filename)
        total_score = sum(plot_scores)

        skip_next_checkpoint_save = True
        print(f"Loaded state from from {checkpoint_filename}")
    else:
        print("No checkpoint file found. Starting from scratch")

    # get latest checkpoint
    game = Game(
        width=width,
        height=height,
        fps=1_000_000_000,
        game_duration_frames=game_duration_frames,
    )
    game.reset_game()
    dt = 1 / fps
    frame_count = 0
    total_reward = 0
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, game_over, score = game.play_step(dt, final_move)
        state_new = agent.get_state(game)
        total_reward += reward
        frame_count += 1

        if frame_count >= game_duration_frames:
            game_over = True

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        # remmeber
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory
            game.reset_game()
            agent.n_games += 1
            frame_count = 0
            agent.train_long_memory()

            if score > record:
                record = score
                if not skip_next_checkpoint_save:
                    agent.save_checkpoint(
                        f"{score:04}_checkpoint", plot_scores, plot_mean_scores
                    )
                skip_next_checkpoint_save = False

            print(f"Game {agent.n_games}, {score=}, {record=}, {total_reward=}")

            total_reward = 0

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


def play(width: int, height: int, fps: int, game_duration_frames: int) -> None:
    agent = Agent()
    checkpoint_filename = get_latest_checkpoint_filename()
    if checkpoint_filename:
        agent.load_checkpoint(checkpoint_filename, train=False)

    game = Game(
        width=width, height=height, fps=fps, game_duration_frames=game_duration_frames
    )
    game.reset_game()
    dt = 1 / fps
    frame_count = 0
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        _, game_over, score = game.play_step(dt, final_move)

        if frame_count >= game_duration_frames:
            game_over = True

        if game_over:
            print(f"Game over! {score=}")
            game.reset_game()
            frame_count = 0

        frame_count += 1


def play_human(width: int, height: int, fps: int, game_duration_frames: int) -> None:
    game = Game(
        width=width, height=height, fps=fps, game_duration_frames=game_duration_frames
    )
    game.reset_game()
    dt = 1 / fps
    frame_count = 0
    while True:
        final_move = game.parse_keys()
        _, game_over, score = game.play_step(dt, final_move)

        if frame_count >= game_duration_frames:
            game_over = True

        if game_over:
            print(f"Game over! {score=}")
            game.reset_game()
            frame_count = 0

        frame_count += 1


def get_latest_checkpoint_filename(directory: str = "checkpoints") -> str:
    files = os.listdir(directory)
    try:
        latest_file = sorted(files)[-1]
        return os.path.join(f"./{directory}", latest_file)
    except IndexError:
        return ""
