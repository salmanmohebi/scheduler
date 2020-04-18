import gym
import scheduler

if __name__ == '__main__':
    env = gym.make("SimpleServicePeriodAllocation-v0")
    env.reset()
    env.step(action=1)


