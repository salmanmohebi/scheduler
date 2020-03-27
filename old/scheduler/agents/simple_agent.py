import numpy as np


class SimpleAgent:
    def __init__(self, env):
        self.epsilon = 0.95
        self.alpha = 0.9
        self.gamma = 0.9
        self.env = env
        self.q_table = np.zeros((env.states_number, env.action_space.n))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return self.env.action_space.sample()
        return np.argmax(self.q_table[state, :])

    def update_table(self, state, action, reward):
        # TODO: should complete
        old_value = self.q_table[state, action]

        self.q_table[state, action] = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
