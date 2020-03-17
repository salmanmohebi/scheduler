import gym
import numpy as np

from scheduler.agents.simple_agent import SimpleAgent

n_eps = 1
t_max = 2
epsilon = 0.9
alpha = 0.9
gamma = 0.9

for ep in range(n_eps):  # Run episodes
    env = gym.make(
        'ServicePeriodAllocation-v0',
        dti_duration=100
    )

    # agent = SimpleAgent(env)
    reward = 0
    state = env.reset()
    q_table = np.zeros((env.states_number, env.action_space.n))
    for t in range(t_max):
        if np.random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()  # Explore action space
        else:
            action = np.argmax(q_table[state])  # Exploit learned values

        next_state, reward, done, info = env.step(action)

        old_value = q_table[state, action]
        next_max = np.max(q_table[next_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value

        state = next_state
        t += 1
        # print(f'reward: {reward}, action: {action}')


        # action = agent.act(state)
        # next_state, reward, done, _ = env.step(action)
        # agent.update_table(state, action, reward)
        #
        # ##################################################
        # old_value = q_table[state, action]
        # next_max = np.max(q_table[next_state])
        #
        # new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        # q_table[state, action] = new_value
        #
        # state = next_state
        # ##################################################
        #
        #
        #
        #
        #
        # if done:
        #     break
        # t += 1
    env.close()
