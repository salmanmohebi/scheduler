import numpy as np
import simpy
from gym import spaces, Env


class ServicePeriodAllocationV1(Env):

    def __init__(self, dti_duration=100, t_max=1000):
        self.dti_duration = dti_duration
        self.alc_period = None
        self.alc_duration = None

        self.env = None  # simpy environment
        self.t_max = t_max
        self.t = 0

        self.verbose = False  # enable logging

        # traffic specification
        self.pkt_generation_period = 10
        self.number_of_pkts = 4
        self.pkt_size = 256
        self.delay_bound = 30
        self.max_buffer_size = 100
        self.buffer = list()

        self.dropped_pkts = self.wasted_time = self.outdated_pkts = 0

        self.state = None
        self.states_number = (self.max_buffer_size + 1) * (self.delay_bound + 1)
        self.action_space = spaces.Discrete(4)

    def reset(self):
        self.alc_duration = np.random.randint(1, self.dti_duration//2)
        self.alc_period = np.random.randint(self.alc_duration, self.dti_duration - self.alc_duration)
        # print(f'duration: {self.alc_duration}, period: {self.alc_period}')
        self._generate_traffic()
        self.dropped_pkts = self.wasted_time = self.outdated_pkts = 0
        self._update_state()
        return self.state

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

        if self.alc_duration == self.alc_period:
            self.alc_duration = self.alc_period = self.dti_duration
        self.dropped_pkts = self.wasted_time = self.outdated_pkts = 0

        # Periodically generate and transmit traffic
        self.env = simpy.Environment(initial_time=self.t*self.dti_duration)
        self.env.process(self._generate_traffic())  # generate traffics
        self.env.process(self._transmit_traffic(self.alc_duration))  # transmit traffic
        self.env.run(until=self.now + self.dti_duration)
        self.t += 1
        reward = self._calculate_reward()
        print(
            f'duration: {self.alc_duration}, period: {self.alc_period}, '
            f'reward: {reward} = {self.wasted_time} (w) + {self.dropped_pkts} (d) + {self.outdated_pkts} (o)'
        )
        self.dropped_pkts = self.wasted_time = 0

        self._update_state()
        return self.state, reward, self.t >= self.t_max, {}

    def render(self, mode='human'):
        pass

    def _calculate_reward(self):
        return -(self.wasted_time + self.dropped_pkts + self.outdated_pkts)

    def _update_state(self):
        self.state = int(self.buffer_size * self.delay_bound + self.oldest_packet)

    @property
    def oldest_packet(self):
        return self.buffer[0].age(self.now) if self.buffer_size > 0 else 0

    @property
    def buffer_size(self):
        return len(self.buffer)

    @property
    def now(self):
        return self.env.now

    def _generate_traffic(self):
        """"Generate periodic traffics

        `self.number_of_pkts` packet generated in every `self.pkt_generation_period`
        The maximum buffer size is `max_buffer_size`
        The number of dropped packets saved in: `self.dropped_pkts`
        """

        while True:
            self._remove_outdated()
            pkts = min(self.number_of_pkts, self.max_buffer_size - self.buffer_size)
            self.buffer.extend([Packet(self.now) for _ in range(pkts)])
            dropped_pkts = self.number_of_pkts - pkts
            self.dropped_pkts += dropped_pkts
            if self.verbose:
                print(f'In {float(self.now)}, {pkts} added to buffer and {dropped_pkts}({self.dropped_pkts}) dropped, size: {self.buffer_size}')
            yield self.env.timeout(self.pkt_generation_period)

    def _transmit_traffic(self, duration, bandwidth=256):
        """ Transmit the packets in buffer in every `self.alc_period` period

        wasted channel time saved in: `self.wasted_time`

        :param duration: Transmission time in each period
        :param bandwidth: Available bandwidth per time unit
        """

        while True:
            available_bandwidth = duration * bandwidth
            while available_bandwidth >= self.pkt_size:
                available_bandwidth -= self.pkt_size
                self._remove_outdated()
                packet_time = self.pkt_size / bandwidth
                if self.buffer_size > 0:
                    self.buffer.pop()
                    if self.verbose:
                        print(f'In {float(self.now)}, 1 packet transmitted, size: {self.buffer_size}')
                else:
                    self.wasted_time += packet_time
                    if self.verbose:
                        print(f'In {float(self.now)}, {float(packet_time)} of time wasted, total: {self.wasted_time}')
                yield self.env.timeout(packet_time)
            yield self.env.timeout(self.alc_period - duration)
            assert self.alc_period != duration

    def _remove_outdated(self):
        """Check and remove the outdated packets from the buffer
        This function should be called before generating new packets and transmit packets
        to remove outdated packets
        """

        size = self.buffer_size
        self.buffer = [packet for packet in self.buffer if packet.age(self.now) <= self.delay_bound]
        self.outdated_pkts += size - self.buffer_size
        if self.verbose and size - self.buffer_size > 0:
            print(f'In {float(self.now)}, {size - self.buffer_size} outdated packets removed, the buffer size: {self.buffer_size}')


class Packet:
    """The packet class,
    A class for packets is more flexible than adding multiple list for traffic
    """
    
    def __init__(self, generated_time, size=256):
        self.time = generated_time
        self.size = size

    def age(self, now):
        return now - self.time
