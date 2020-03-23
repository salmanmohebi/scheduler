import random
import logging.config

import simpy
import numpy as np
from gym import spaces, Env


class DtiAllocationV0(Env):
    def __init__(self):
        self.env = None
        self.number_of_stations = 7
        self.pkt_size = 1472
        self.max_q_size = 5000
        self.mcs_throughput = 3465
        self.bi_duration = 0.041984
        self.possible_data_rate = np.array([50, 100, 150, 200, 600], dtype=np.float64)
        self.stations_data_rate = np.array(
            [np.random.choice(self.possible_data_rate) * 10 ** 6 for _ in range(self.number_of_stations)]
        )  # data rate for each station

        # min required SP for each station
        self.min_sp = (self.stations_data_rate / self.mcs_throughput) * self.bi_duration * 10 ** 6
        self.pkt_generation_period = (self.pkt_size/self.stations_data_rate) * 10 ** 6
        self.verbose = False
        self.dropped_pkts = self.wasted_time = self.outdated_pkts = 0
        self.t = 0

        self.number_of_actions = 10
        # TODO: action and observation spaces anre not continues, can use spaces.discrete()
        self.action_space = spaces.Box(low=0, high=self.number_of_actions, shape=(self.number_of_stations,), dtype=int)
        self.observation_space = spaces.Box(low=0, high=self.max_q_size, shape=(self.number_of_stations,), dtype=int)

        self.queue_size = np.zeros(self.number_of_stations)  # for all stations
        self.sp_duration = self.min_sp
        self.sp_start = None

    def reset(self):
        self.dropped_pkts = self.wasted_time = self.outdated_pkts = 0
        self.queue_size = np.zeros(self.number_of_stations)
        return self.queue_size

    def step(self, action):
        print(f'STEP: {self.t}')
        self.env = simpy.Environment(initial_time=self.t * self.bi_duration * 10 ** 6)  # simpy environment

        self.sp_duration = self.min_sp * (1 + action / 10)
        self.sp_start = np.concatenate(([0], np.cumsum(self.sp_duration)[:-1]))

        for idx in range(self.number_of_stations):
            self.env.process(self._transmit_traffic(idx, self.sp_start[idx], self.sp_duration[idx]))
        for idx in range(self.number_of_stations):
            self.env.process(self._generate_traffic(idx))

        # self.env.run(self.bi_duration * 10**6)
        self.env.run(until=self.now + self.bi_duration * 10**6)
        self.t += 1
        return self.queue_size, self._calculate_rewards(), False, {}

    def render(self, mode='human', close=False):
        return

    def _calculate_rewards(self):
        # TODO: Calculate reward
        return np.zeros(self.number_of_stations)

    def _generate_traffic(self, idx):
        while True:
            if self.queue_size[idx] < self.max_q_size - 1:
                self.queue_size[idx] += 1
                if self.verbose:
                    print(f'TIME: {self.now}: station {idx} , new packet , queue size: {self.queue_size[idx]}')
            else:
                self.dropped_pkts += 1
            yield self.env.timeout(self.pkt_generation_period[idx])

    def _transmit_traffic(self, idx, start, duration):
        print(f'TIME: {self.now}: station {idx}, scheduled: start {start}, duration: {duration}')
        yield self.env.timeout(start)
        print(f'TIME: {self.now}: station {idx}, SP start')
        available_bandwidth = self.mcs_throughput * duration
        while available_bandwidth >= self.pkt_size:
            available_bandwidth -= self.pkt_size
            packet_time = self.pkt_size / self.mcs_throughput
            if self.queue_size[idx] > 0:
                self.queue_size[idx] -= 1
                if self.verbose:
                    print(f'TIME: {self.now}: station {idx}, packet transmitted, size: {self.queue_size[idx]}')
            else:
                self.wasted_time += 1
                if self.verbose:
                    print(f'TIME: {self.now}: station {idx}, time wasted, total: {self.wasted_time}')
            yield self.env.timeout(packet_time)

    def _remove_outdated(self, delay_bound):  # TODO: this function doesn't use for now
        """Check and remove the outdated packets from the buffer
        This function should be called before generating new packets and transmit packets
        to remove outdated packets
        """

        size = self.buffer_size
        self.buffer = [packet for packet in self.buffer if packet.age(self.now) <= delay_bound]
        self.outdated_pkts += size - self.buffer_size
        if self.verbose and size - self.buffer_size > 0:
            print(
                f'In {float(self.now)}, {size - self.buffer_size} outdated packets removed, the buffer size: {self.buffer_size}')

    @property
    def buffer_size(self):
        return len(self.buffer)

    @property
    def now(self):
        return self.env.now
