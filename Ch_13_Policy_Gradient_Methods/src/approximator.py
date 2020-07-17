import torch
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn

class NN(nn.Module):
    """Neural network to approximate the value function."""

    def __init__(self, input_size):
        super(NN, self).__init__()
        self.l1 = nn.Linear(input_size, 10)
        self.l2 = nn.Linear(10, 1)

    def forward(self, x):
        x = F.relu(self.l1(x))
        x = self.l2(x)
        return x

