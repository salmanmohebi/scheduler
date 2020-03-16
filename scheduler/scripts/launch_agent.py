import gym

from scheduler.agents.simple_agent import SimpleAgent


n_eps = 16
t_max = 200

for ep in range(n_eps):  # Run episodes
    env = gym.make('ServicePeriodAllocation-v0')  # Init environment

    agent = SimpleAgent(env)
    reward = 0
    done = False
    state = env.reset()
    for t in range(t_max):
        action = agent.act(state, reward, done)
        state, reward, done, _ = env.step(action)
        if done:
            break
    env.close()
