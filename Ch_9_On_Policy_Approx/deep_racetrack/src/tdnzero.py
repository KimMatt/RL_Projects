import numpy as np

import math

import torch
import torch.optim as optim
import torch.nn.functional as F

from src.network import NN

from game.racetrack import RaceTrack


class Agent:

    position = None
    track = None
    velocity = None
    values = None

    def __init__(self):
        """Initialize our agent's parameters and data stores
        """
        self.track = RaceTrack()
        self.eps_start = 0.9
        self.eps_end = 0.2
        self.eps_decay = 50000
        self.discount_rate = 0.95
        self.actions = []
        self.velocity = np.array([0, 0])
        for i in [1, 0, -1]:
            for j in [1, 0, -1]:
                self.actions.append(np.array([i, j]))
        self.values = NN()
        self.optimizer = optim.RMSprop(self.values.parameters())
        self.reset()

    def bind_velocity(self, velocity):
        """Bind our agent's velocities according to "speed limits"
        """
        if velocity[0] >= 5:
            velocity[0] = 4
        if velocity[0] < 0:
            velocity[0] = 0
        if velocity[1] <= -5:
            velocity[1] = -4
        if velocity[1] > 0:
            velocity[1] = 0
        return velocity

    def select_action(self):
        """Select an action using epsilon greedy policy

        Returns:
            [action]: select action
        """
        # if not exploiting select the max action
        eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * \
            math.exp(-1. * self.t / self.eps_decay)
        if np.random.rand() > eps_threshold:
            next_velocities = [self.bind_velocity(
                self.velocity + action) for action in self.actions]
            # construct after-states of using each action
            next_states = torch.tensor(
                [[self.position[0], self.position[1], velocity[0], velocity[1]] for velocity in next_velocities], dtype=torch.float)
            with torch.no_grad():
                output = self.values(next_states)
            # find which action selection leads to the best after-state
            max_value = None
            max_value_index = None
            for index, value in enumerate(output):
                if max_value is None or value[0] > max_value:
                    max_value = value[0]
                    max_value_index = index
            # the action to value ordering should be retained in the output ordering
            action = self.actions[max_value_index]
        else:
            # if exploring select an action at random
            random = np.random.randint(0, len(self.actions))
            action = np.array(self.actions[random])
        return action

    def play(self, mode=None):
        """Play a move on the racetrack, selecting an action
        Returns:
            [reward]: integer for reward from this time step
        """
        reward, next_position, next_velocity = self.track.time_step(
            self.position, self.velocity)
        state = torch.tensor(
            [[self.position[0], self.position[1], self.velocity[0], self.velocity[1]]], dtype=torch.float)
        # update position and velocity according to environment interaction
        self.position = next_position
        self.velocity = next_velocity
        # choose next action
        self.action = self.select_action()
        self.velocity = self.bind_velocity(np.add(self.velocity, self.action))
        next_state = torch.tensor(
            [[self.position[0], self.position[1], self.velocity[0], self.velocity[1]]], dtype=torch.float)
        state_approx = self.values(state)
        updated_approx = reward + (self.discount_rate * self.values(next_state))
        # calculate loss between most local state-value and approximated
        loss = F.smooth_l1_loss(state_approx, updated_approx)
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.values.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()
        # update time step
        self.t += 1
        return reward

    def reset(self):
        """Reset the agent's episode-dependent parameters
        """
        self.t = 0
        self.position = self.track.get_starting_position()
        self.velocity = np.array([0, 0])
        self.action = self.select_action()
        self.velocity = self.bind_velocity(np.add(self.velocity, self.action))
