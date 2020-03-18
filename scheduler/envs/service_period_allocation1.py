import numpy as np
from gym import spaces, Env


class ServicePeriodAllocationV1(Env):

    def __init__(self, dti_duration=100, t_max=1000):
        self.dti_duration = dti_duration
        self.alc_period = None
        self.alc_duration = None

        self.time = 0
        self.t_max = t_max
        self.t = 0

        self.last_packet_time = 0

        # traffic specification
        self.packet_generation_period = 10
        self.number_of_packets = 4
        self.maximum_queue_length = 100
        self.first_packet_time = 0
        self.packet_size = 256
        self.buffer_size = 0

        self.dropped_packets = self.wasted_bandwidth = 0

        self.states_number = self.maximum_queue_length
        self.action_space = spaces.Discrete(2)

    def reset(self):
        self.alc_duration = np.random.randint(1, self.dti_duration//2)
        self.alc_period = np.random.randint(self.alc_duration, self.dti_duration - self.alc_duration)
        print(f'duration: {self.alc_duration}, period: {self.alc_period}')
        self._update_queue()
        self.dropped_packets = self.wasted_bandwidth = 0
        return self.buffer_size

    def step(self, action):
        # if action == 0:
        #     self.alc_duration -= self.alc_duration // 10 + 1
        #     self.alc_period -= self.alc_period // 10 + 1
        # elif action == 1:
        #     self.alc_duration += self.alc_duration // 10
        #     self.alc_period -= self.alc_period // 10 + 1
        # elif action == 2:
        #     self.alc_duration -= self.alc_duration // 10 + 1
        #     self.alc_period += self.alc_period // 10
        # elif action == 3:
        #     self.alc_duration += self.alc_duration // 10
        #     self.alc_period += self.alc_period // 10
        #
        # if self.alc_duration < 1:
        #     self.alc_duration = 1
        # if self.alc_period < self.alc_duration:
        #     self.alc_period = self.alc_duration

        for t in range(0, self.dti_duration, self.alc_period):
            # print(f'in time {t},')
            self.time = t
            self._update_queue()
            self._transmit_traffic(self.alc_duration)
        self.t += 1
        reward = self._calculate_reward()

        # print(f'{self.alc_duration}, {self.alc_period}: reward: {reward} = {self.dropped_packets}+{self.wasted_bandwidth}')
        self.dropped_packets = self.wasted_bandwidth = 0

        return self.buffer_size, reward, self.t >= self.t_max, {}

    def render(self, mode='human'):
        pass

    def _calculate_reward(self):
        return -(self.wasted_bandwidth + self.dropped_packets)

    def _update_queue(self):
        for t in range(self.last_packet_time, self.time, self.packet_generation_period):
            pkts = min(self.number_of_packets, self.maximum_queue_length - self.buffer_size)
            self.buffer_size += pkts
            dropped_packets = self.number_of_packets - pkts
            self.dropped_packets += dropped_packets
            self.last_packet_time += self.packet_generation_period
            print(f' in {t}, {pkts} added to buffer, new size is: {self.buffer_size}')

    def _transmit_traffic(self, duration, bandwidth=256):
        available_bandwidth = duration * bandwidth
        data_rate = available_bandwidth // self.packet_size
        pkts = min(data_rate, self.buffer_size)
        available_bandwidth -= pkts * self.packet_size
        self.buffer_size -= pkts
        self.wasted_bandwidth += available_bandwidth/self.packet_size
        if pkts > 0:
            print(f' in {self.time}, {pkts} transmitted, new size is: {self.buffer_size}')
