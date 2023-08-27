from src.game.game import Game


class Agent:
    def __init__(self, game: Game) -> None:
        self.game = game

    def play_game_many_times(self, n_replays: int) -> None:
        for _ in range(n_replays):
            self.game.new_game()
            self.game.run()
