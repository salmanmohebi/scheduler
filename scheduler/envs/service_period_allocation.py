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

    def age(self, time):
        return time - self.generated_time


class ConstantBitRateTraffic:
    def __init__(
            self,
            packet_generation_period=30,
            maximum_generated_packet=4,
            maximum_queue_length=100,
            delay_bound=100,
            first_packet_time=2
    ):
        self.packet_generation_period = packet_generation_period
        self.maximum_generated_packet = maximum_generated_packet
        self.maximum_queue_length = maximum_queue_length
        self.delay_bound = delay_bound
        self.first_packet_time = first_packet_time
        self.last_packet_time = self.first_packet_time
        self.queue = list()

    def generate_data(self, time):
        for t in range(self.last_packet_time, time, self.packet_generation_period):
            self.last_packet_time = t
            for p in range(np.random.randint(1, self.maximum_generated_packet)):
                if len(self.queue) < self.maximum_queue_length:
                    self.queue.append(Packet(t))
                    print(f'New packet added to queue, at {t}, the length of queue is: {len(self.queue)}')
                else:
                    print(f'Queue overflowed at {t}  should do some thing')
                    # TODO: Record the number of dropped packets to punish the agent
        self.last_packet_time += self.packet_generation_period

    def delete_outdated_packets(self, time):
        old_queue_size = len(self.queue)
        self.queue = [p for p in self.queue if p.age(time) <= self.delay_bound]
        print(f' #{old_queue_size - len(self.queue)} outdated packets dropped')
        # TODO: Record the number of dropped packets to punish the agent
