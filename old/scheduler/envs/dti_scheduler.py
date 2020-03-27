import simpy
import numpy as np
from gym import spaces, Env


class DtiAllocationV0(Env):
    def __init__(self):
        self.env = self.env = simpy.Environment()  # simpy environment

        # Traffic specifics
        self.number_of_stations = 4
        self.packet_size = 1472  # Byte
        self.max_q_size = 5000
        self.queue_size = np.zeros(self.number_of_stations)  # Save the size of queue for stations
        self.batch_size = 100 * np.ones((self.number_of_stations,))  # Number of packets in each period
        self.possible_data_rate = np.array([20, 50, 100, 150, 200], dtype=np.float64) * 10 ** 6  # MBps
        self.stations_data_rate = np.array(
            [np.random.choice(self.possible_data_rate) for _ in range(self.number_of_stations)]
        )  # data rate for each station, MBps
        self.pkt_generation_period = self.batch_size * self.packet_size/self.stations_data_rate  # Seconds

        self.channel_throughput = 4620 * 10 ** 6  # channel throughput (MCS12), bps

        self.bi_duration = 0.041984  # Seconds

        # Record some statistics for future uses
        self.dropped_pkts, self.wasted_resources, self.outdated_pkts, self.successful_transmission =\
            np.zeros((4, self.number_of_stations))

        self.t = 0  # count the steps
        self.verbose = True  # print logging

        self.min_sp = None  # min required SP for each station, Seconds
        self.sp_duration = None
        self.sp_start = None

        self.number_of_actions = 10
        self.action_space = spaces.Box(
            low=0, high=self.number_of_actions, shape=(self.number_of_stations,), dtype=int
        )
        self.observation_space = spaces.Box(
            low=0, high=self.max_q_size, shape=(self.number_of_stations,), dtype=int
        )

    def reset(self):
        # Update environment parameters
        self._update_env()

        # Initialize the packet generation functions for stations
        for idx in range(self.number_of_stations):
            self.env.process(self._generate_traffic(idx))
        return self.queue_size

    def step(self, action):
        print(f'STEP: {self.t} started')

        # Update environment parameters
        self._update_env()
        assert isinstance(action, (np.ndarray, np.generic))
        # update SPs duration
        self.sp_duration = self.min_sp * (1 + action / 10)
        # calculate SPs starting time
        self.sp_start = np.concatenate(([0], np.cumsum(self.sp_duration)[:-1]))

        #  schedule the SP for stations in queues based on FCFS
        for idx in range(self.number_of_stations):
            self.env.process(self._transmit_traffic(idx, self.sp_start[idx], self.sp_duration[idx]))

        # Run for one episode
        self.env.run(until=self.now + self.bi_duration)
        self.t += 1

        return self.queue_size, self._calculate_rewards(), False, {}

    def render(self, mode='human', close=False):
        return

    def _update_env(self):
        self.dropped_pkts, self.wasted_resources, self.outdated_pkts, self.successful_transmission = \
            np.zeros((4, self.number_of_stations))

        # generate packets based on poisson distribution
        self.batch_size = np.random.poisson(100, self.number_of_stations)
        #  TODO: the bi_duration is static for now, but it can change over steps
        self.min_sp = (self.stations_data_rate * 8 / self.channel_throughput) * self.bi_duration

    def _calculate_rewards(self):
        # TODO: Calculate reward
        return np.zeros(self.number_of_stations)

    def _generate_traffic(self, idx):
        """
        generate periodic traffics: `self.batch_size[idx]` packets
        in every `self.pkt_generation_period[idx]` seconds
        :param idx: station Id
        :return:
        """
        if self.verbose:
            print(f'Station {idx}, is generating {self.batch_size[idx]} '
                  f'in every {self.pkt_generation_period[idx]: .9f} seconds')

        while True:
            new_packets = min(self.batch_size[idx], self.max_q_size - self.queue_size[idx] - 1)
            self.queue_size[idx] += new_packets
            self.dropped_pkts[idx] += self.batch_size[idx] - new_packets
            assert self.queue_size[idx] < self.max_q_size
            assert self.pkt_generation_period[idx] > 0
            yield self.env.timeout(self.pkt_generation_period[idx])

    def _transmit_traffic(self, idx, start, duration):
        """
        Transmit traffic over the channel, with `self.channel_throughput`
        bandwidth for `duration` seconds
        :param idx: station Id
        :param start: SP starting time
        :param duration: SP duration
        :return:
        """

        yield self.env.timeout(start)
        if self.verbose:
            print(f'TIME: {self.now: .9f} station {idx}, '
                  f'service period (SP) started for {duration: .9f} seconds')

        available_bandwidth = duration * self.channel_throughput
        packet_size_bit = self.packet_size * 8

        while available_bandwidth >= packet_size_bit:
            available_bandwidth -= packet_size_bit
            packet_transmit_time = packet_size_bit / self.channel_throughput

            if self.queue_size[idx] > 0:
                self.queue_size[idx] -= 1
                self.successful_transmission[idx] += 1

            else:
                self.wasted_resources[idx] += 1
            # TODO: transmit until the end of duration or nex packet generating instead of packet by packet
            assert packet_transmit_time > 0
            yield self.env.timeout(packet_transmit_time)

        if self.verbose:
            print(f'TIME: {self.now: .9f} station {idx}, SP ended, {self.successful_transmission[idx]}'
                  f' packet transmitted, {self.wasted_resources[idx]} resource wasted')

    def _remove_outdated(self, delay_bound):  # TODO: this function doesn't used for now
        """Check and remove the outdated packets from the buffer
        This function should be called before generating new packets and transmit packets
        to remove outdated packets
        """

        size = self.buffer_size

        self.buffer = [packet for packet in self.buffer if packet.age(self.now) <= delay_bound]
        self.outdated_pkts += size - self.buffer_size

        if self.verbose and size - self.buffer_size > 0:
            print(f'In {float(self.now)}, {size - self.buffer_size} outdated packets removed,'
                  f' the buffer size: {self.buffer_size}')

    @property
    def buffer_size(self):
        return len(self.buffer)

    @property
    def now(self):
        return self.env.now
