import math
import numpy as np


class RaceTrack:

    states = None

    def __init__(self):
        race_map = open("./game/maps/map.bin", "r")
        lines = race_map.readlines()
        self.states = {}
        # cheat
        # taking into account the /n character
        self.f_line = len(lines[0]) - 2
        self.start_positions = []

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "\n" and int(char) == 1:
                    self.states[str(np.array([x, y]))] = np.array([x, y])
                    if y == len(lines) - 1:
                        self.start_positions.append(np.array([x, y]))

    def get_starting_position(self):
        start_position = np.random.randint(0, len(self.start_positions))
        return self.start_positions[start_position]

    def check_f_line_legal_cross(self, start_pos, end_pos):
        """check if the f_line was crossed legally meaning the agent didn't
            go out of the map's boundaries

        Args:
            start_pos ([x,y]): the starting position of the move before time_step was applied
            end_pos ([x,y]): where it ended up, before any correction

        Returns:
            result, y_coord: whether or not it was a legal cross and if so, the y coordinate
        """
        if end_pos[0] >= self.f_line:
            # height
            y_dist = abs(start_pos[1] - end_pos[1])
            if y_dist == 0 or end_pos[0] == self.f_line:
                y_intercept = end_pos[1]
            else:
                # width
                x_dist = abs(start_pos[0] - end_pos[0])
                # |\ the top angle
                angle = math.atan(x_dist/y_dist)
                # horizontal distance between finish line and start line
                x_intercept_dist = abs(self.f_line - start_pos[0])
                y_intercept_dist = x_intercept_dist / math.tan(angle)
                sign = 1 if start_pos[1] < end_pos[1] else -1
                y_intercept = start_pos[1] + (sign * y_intercept_dist)
            if y_intercept >= 0 and y_intercept <= 5:
                return True, math.floor(y_intercept)
        return False, None

    def time_step(self, position, velocities):
        """carry out a time step on our track given position and velocity

        Args:
            position ([x,y]): state coordinate
            velocities ([type]): velocity from an action

        Returns:
            reward: integer reward
            new_position: resulting state
            velocities: resulting velocity (only changed if back to start)
        """
        new_position = np.add(velocities, position)
        # to correct for overshooting the finish line
        legal_cross, y_intercept = self.check_f_line_legal_cross(
            position, new_position)
        if legal_cross:
            new_position[0] = self.f_line
            new_position[1] = y_intercept
        if self.states.get(str(np.array(new_position))) is None:
            new_position = self.get_starting_position()
            velocities = np.array([0, 0])
        reward = 1 if position[0] == self.f_line else 0
        return reward, new_position, velocities
