import torch
from torch import nn, optim, Tensor
from torch.nn import functional as F
import os
from typing import List, Tuple

from src.types.actionarr import ActionArr, StateArr


class Linear_QNet(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: Tensor) -> Tensor:
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name: str = "model.pth") -> None:
        model_folder_path = "./model"
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_path = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_path)


class QTrainer:
    def __init__(self, model: nn.Module, lr: float, gamma: float):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_single_step(
        self,
        state: StateArr,
        action: ActionArr,
        reward: int,
        next_state: StateArr,
        game_over: bool,
    ) -> None:
        self.train_step(
            [state],
            [action],
            [reward],
            [next_state],
            (game_over,),
        )

    def train_step(
        self,
        state: List[StateArr],
        action: List[ActionArr],
        reward: List[int],
        next_state: List[StateArr],
        game_over: Tuple[bool],
    ) -> None:
        state0 = torch.tensor(state, dtype=torch.float)
        action0 = torch.tensor(action, dtype=torch.float)
        reward0 = torch.tensor(reward, dtype=torch.float)
        next_state0 = torch.tensor(next_state, dtype=torch.float)
        game_over0 = game_over

        # 1: predict
        pred = self.model(state0)

        target = pred.clone()

        for idx in range(len(game_over0)):
            Q_new = reward0[idx]
            if not game_over0[idx]:
                Q_new = reward0[idx] + self.gamma * torch.max(
                    self.model(next_state0[idx])
                )
            target[idx][torch.argmax(action0).item()] = Q_new

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this i fnot done
        # pred.clone()
        # preds[argmax(action)] = Q_new

        # Calc loss
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
