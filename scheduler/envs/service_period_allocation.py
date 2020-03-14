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


class Packet:
    def __init__(self, time):
        self.generated_time = time
        self.packet_size = 256
        self.delay_bound = 100

    def age(self, time):
        return time - self.generated_time


class ConstantBitRateTraffic:
    def __init__(
            self,
            packet_generation_period=30,
            maximum_generated_packet=40,
            maximum_queue_length=100
    ):
        self.packet_generation_period = packet_generation_period
        self.maximum_generated_packet = maximum_generated_packet
        self.maximum_queue_length = maximum_queue_length
        self.queue = list()

    def generate_data(self, time):
        last_packet_time = self.queue[-1].generated_time if len(self.queue) > 0 else 0
        for t in range(last_packet_time, time, self.packet_generation_period):
            for p in range(np.random.randint(1, self.maximum_generated_packet)):
                if len(self.queue) < self.maximum_queue_length:
                    self.queue.append(Packet(t))
                    print(f'New packet added to queue, the length of queue is: {len(self.queue)}')
                else:
                    print('Queue overflow, should do some thing')
                    # Record the number of dropped packets to punish agent





