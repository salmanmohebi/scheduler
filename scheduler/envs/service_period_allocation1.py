import numpy as np
import simpy
from gym import spaces, Env


class ServicePeriodAllocationV1(Env):

    def __init__(self, dti_duration=100, t_max=1000):
        self.env = None
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
        self.max_buffer_size = 99
        self.first_packet_time = 0
        self.packet_size = 256
        self.buffer_size = 0

        self.dropped_packets = self.wasted_time = 0

        self.states_number = self.max_buffer_size + 1
        self.action_space = spaces.Discrete(4)

    def reset(self):
        self.alc_duration = np.random.randint(1, self.dti_duration//2)
        self.alc_period = np.random.randint(self.alc_duration, self.dti_duration - self.alc_duration)
        # print(f'duration: {self.alc_duration}, period: {self.alc_period}')
        self._update_queue()
        self.dropped_packets = self.wasted_time = 0
        return self.buffer_size

    # def step(self, action):
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
        #
        # for t in range(0, self.dti_duration, self.alc_period):
        #     # print(f'in time {t},')
        #     self.time = t
        #     self._update_queue()
        #     self._transmit_traffic(self.alc_duration)
        # self.t += 1
        # reward = self._calculate_reward()
        #
        # # print(f'{self.alc_duration}, {self.alc_period}: reward: {reward} = {self.dropped_packets}+{self.wasted_time}')
        # self.dropped_packets = self.wasted_time = 0
        #
        # return self.buffer_size, reward, self.t >= self.t_max, {}

    def step(self, action):
        if action == 0:
            self.alc_duration -= self.alc_duration // 10 + 1
            self.alc_period -= self.alc_period // 10 + 1
        elif action == 1:
            self.alc_duration += self.alc_duration // 10
            self.alc_period -= self.alc_period // 10 + 1
        elif action == 2:
            self.alc_duration -= self.alc_duration // 10 + 1
            self.alc_period += self.alc_period // 10
        elif action == 3:
            self.alc_duration += self.alc_duration // 10
            self.alc_period += self.alc_period // 10

        if self.alc_duration < 1:
            self.alc_duration = 1
        if self.alc_duration > self.dti_duration//2:
            self.alc_duration = self.dti_duration//2
        if self.alc_period > self.dti_duration:
            self.alc_period = self.dti_duration
        if self.alc_period < self.alc_duration:
            self.alc_period = self.alc_duration

        self.dropped_packets = self.wasted_time = 0
        self.env = simpy.Environment()
        self.env.process(self._update_queue())
        self.env.process(self._transmit_traffic(self.alc_duration))
        self.env.run(until=self.dti_duration)

        self.t += 1
        reward = self._calculate_reward()
        print(f'duration: {self.alc_duration}, period: {self.alc_period}, reward: {reward} = {self.wasted_time}w + {self.dropped_packets}d')
        # print(f'{self.alc_duration}, {self.alc_period}: reward: {reward} = {self.dropped_packets}+{self.wasted_time}')
        self.dropped_packets = self.wasted_time = 0

        return self.buffer_size, reward, self.t >= self.t_max, {}

    def render(self, mode='human'):
        pass

    def _calculate_reward(self):
        return -(self.wasted_time + self.dropped_packets)

    def _update_queue(self):
        while True:
            pkts = min(self.number_of_packets, self.max_buffer_size - self.buffer_size)
            self.buffer_size += pkts
            dropped_packets = self.number_of_packets - pkts
            self.dropped_packets += dropped_packets
            self.last_packet_time += self.packet_generation_period
            # print(f'In {float(self.env.now)}, {pkts} added to buffer and {dropped_packets}({self.dropped_packets}) dropped, size: {self.buffer_size}')
            yield self.env.timeout(self.packet_generation_period)

    def _transmit_traffic(self, duration, bandwidth=256):
        while True:
            available_bandwidth = duration * bandwidth
            while available_bandwidth > self.packet_size:
                available_bandwidth -= self.packet_size
                packet_time = self.packet_size / bandwidth
                if self.buffer_size > 0:
                    self.buffer_size -= 1
                    # print(f'In {float(self.env.now)}, 1 packet transmitted, size: {self.buffer_size}')
                else:
                    self.wasted_time += packet_time
                    # print(f'In {float(self.env.now)}, {float(packet_time)} of time wasted, total: {self.wasted_time}')
                yield self.env.timeout(packet_time)
            yield self.env.timeout(self.alc_period)
