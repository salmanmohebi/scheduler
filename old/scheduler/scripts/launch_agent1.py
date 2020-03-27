import gym
import numpy as np
import random

n_eps = 1000
t_max = 100
alpha = 0.1
gamma = 0.6
epsilon = 0.1

env = gym.make('ServicePeriodAllocation-v1')
q_table = np.zeros((env.states_number, env.action_space.n))

print('lets go...')
for ep in range(n_eps):
    reward = 0
    state = env.reset()
    for t in range(t_max):
        if random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state])
        next_state, reward, done, _ = env.step(action)

        q_value = q_table[state, action]
        max_value = np.max(q_table[next_state])
        new_q_value = (1 - alpha) * q_value + alpha * (reward + gamma * max_value)
        q_table[state, action] = new_q_value
        state = next_state
env.close()
