import gym
import numpy as np
import random

n_eps = 1
t_max = 10
alpha = 0.1
gamma = 0.6
epsilon = 0.1

env = gym.make('DtiAllocation-v0')
q_table = np.zeros((env.number_of_stations, env.max_q_size, env.number_of_actions))

print('lets go...')
for ep in range(n_eps):
    state = env.reset()
    for t in range(t_max):
        for st in range(env.number_of_stations):
            if random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()
            else:
                action = np.zeros(env.number_of_stations)
                action[st] = np.argmax(q_table[st, int(state[st]), :])
            next_state, reward, done, _ = env.step(action)

            q_value = q_table[st, int(state[st]), int(action[st])]
            max_value = np.max(q_table[st, int(next_state[st])])
            new_q_value = (1 - alpha) * q_value + alpha * (reward + gamma * max_value)
            q_table[st, int(state[st]), int(action[st])] = new_q_value[st]
            state = next_state
env.close()

