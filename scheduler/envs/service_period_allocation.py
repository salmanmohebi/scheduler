import numpy as np
from gym import spaces, Env


TIME = None


class ServicePeriodAllocationV0(Env):
    metadata = {
        'render.modes': ['human', 'rgb_array']
    }

    def __init__(self):
        self.allocation_period = None
        self.allocation_duration = None
        self.dti_duration = None

        self.delay_bound = None
        self.maximum_packet_size = None
        self.max_queue_length = None
        self.data_generation_rate = None  # Not useful??
        self.data_generation_period = None

        self.channel_bandwidth = None
        self.channel_bit_loss_rate = None

    def reset(self):
        pass

    def seed(self, seed=0):
        pass

    def step(self, action):
        pass

    def render(self, mode='human', close=False):
        pass


