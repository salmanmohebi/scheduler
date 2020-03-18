import numpy as np
from gym import spaces, Env


TIME = None


class ServicePeriodAllocationV0(Env):

    def __init__(self, dti_duration, channel_bandwidth=None, channel_bit_loss_rate=None, t_max=1000):
        self.dti_duration = dti_duration
        self.allocation_period = None
        self.allocation_duration = None

        self.channel_bandwidth = channel_bandwidth
        self.channel_bit_loss_rate = channel_bit_loss_rate
        self.traffic = None
        self.time = 0
        self.t_max = t_max
        self.t = 0

        # traffic specification
        self.packet_generation_period = 10
        self.number_of_packets = 4
        self.maximum_queue_length = 100
        self.delay_bound = 50
        self.first_packet_time = 0
        self.packet_size = 256

        self.states_number = self.maximum_queue_length*self.delay_bound
        self.action_space = spaces.Discrete(4)

    def reset(self):
        self.traffic = ConstantBitRateTraffic(
            self.packet_generation_period,
            self.number_of_packets,
            self.maximum_queue_length,
            self.delay_bound,
            self.first_packet_time,
            self.packet_size
        )
        self.traffic.update_queue(0)
        self.allocation_duration = np.random.randint(1, self.dti_duration//2)
        self.allocation_period = np.random.randint(
            self.allocation_duration, self.dti_duration - self.allocation_duration
        )
        self._update_state(0)
        return self.state

    def seed(self, seed=0):
        pass

    def step(self, action):
        # TODO: check the overlap between allocations
        # TODO: Too dirty, rewrite it
        self.traffic.dropped_packets_ = 0
        self.traffic.dropped_packets_ = 0
        self.traffic.wasted_bandwidth = 0
        if action == 0:
            self.allocation_duration = max(1, self.allocation_duration - np.math.ceil(self.allocation_duration / 10))
            self.allocation_period = max(self.allocation_duration, self.allocation_period - np.math.ceil(self.allocation_period / 10))
        elif action == 1:
            self.allocation_duration += np.math.ceil(self.allocation_duration / 10)
            self.allocation_period = max(self.allocation_duration, self.allocation_period - np.math.ceil(self.allocation_period / 10))
        elif action == 2:
            self.allocation_duration = max(1, self.allocation_duration - np.math.ceil(self.allocation_duration / 10))
            self.allocation_period += np.math.ceil(self.allocation_period / 10)
        elif action == 3:
            self.allocation_duration += np.math.ceil(self.allocation_duration / 10)
            self.allocation_period += np.math.ceil(self.allocation_period / 10)

        for t in range(self.time, self.time + self.dti_duration, self.allocation_period):
            self.traffic.update_queue(t)
            self.traffic.transmit_traffic(self.allocation_duration, t)
        self.time += self.dti_duration
        self.t += 1
        reward = self._calculate_reward()
        self._update_state(self.time)
        print(f' = {reward} (reward), allocation_duration: {self.allocation_duration}, allocation_preiod: {self.allocation_period}')
        return self.state, reward, self.t >= self.t_max, {}

    def render(self, mode='', close=False):
        pass

    def _calculate_reward(self):
        od = self.traffic.dropped_packets_overflow
        of = self.traffic.dropped_packets_outdated
        wb = self.traffic.wasted_bandwidth
        print(f' - ({of} + {od} + {wb})', end="")
        # self.traffic.dropped_packets_ = 0
        # self.traffic.dropped_packets_ = 0
        # self.traffic.wasted_bandwidth = 0
        return -od - of - wb

    def _update_state(self, time):
        # state space is the age of oldest packet and the q size
        buffer_size = len(self.traffic.queue)
        oldest_packet = self.traffic.queue[0].age(time) if buffer_size > 0 else 0
        # self.state = np.array([buffer_size, oldest_packet])
        # print(f'---{buffer_size} - {oldest_packet}')
        self.state = buffer_size * self.delay_bound + oldest_packet - 1 if buffer_size > 0 and oldest_packet > 0 else 0
        return self.state


class Packet:
    def __init__(self, time, size=256):
        self.generated_time = time
        self.size = size

    def age(self, time):
        return time - self.generated_time


class ConstantBitRateTraffic:
    def __init__(
            self,
            packet_generation_period=30,
            number_of_packets=4,
            maximum_queue_length=100,
            delay_bound=100,
            first_packet_time=0,
            packet_size=256
    ):
        self.packet_generation_period = packet_generation_period
        self.number_of_packets = number_of_packets
        self.maximum_queue_length = maximum_queue_length
        self.delay_bound = delay_bound
        self.first_packet_time = first_packet_time
        self.last_packet_time = self.first_packet_time
        self.queue = list()
        self.dropped_packets_overflow = 0
        self.dropped_packets_outdated = 0
        self.wasted_bandwidth = 0
        self.packet_size = packet_size

    @property
    def qsize(self):
        return len(self.queue)

    def generate_new_packets(self, time):
        new_packets = min(self.number_of_packets, self.maximum_queue_length - self.qsize)
        self.queue.extend([Packet(time, size=self.packet_size) for _ in range(new_packets)])
        # print(f'{new_packets} new packets generated at: {time}, the buffer size: {self.qsize}')
        dropped_packets = self.number_of_packets - new_packets
        self.dropped_packets_overflow += dropped_packets
        # print(f'# {dropped_packets} packet dropped because of overflow, at: {time}')

        self.last_packet_time += self.packet_generation_period

    def delete_outdated_packets(self, time):
        old_queue_size = self.qsize
        self.queue = [p for p in self.queue if p.age(time) < self.delay_bound]
        dropped_packets = old_queue_size - self.qsize
        self.dropped_packets_outdated += dropped_packets
        # print(f'At: {time}, # {dropped_packets} outdated packets dropped, q size: {self.qsize}')

    def update_queue(self, time):
        for t in range(self.last_packet_time, time, self.packet_generation_period):
            self.delete_outdated_packets(t)
            self.generate_new_packets(t)
            self.last_packet_time = t

    def transmit_traffic(self, duration, time, bandwidth=256, bit_error_rate=None):
        # The bandwidth is per time unite not s
        available_bandwidth = duration*bandwidth
        tp = 0
        for packet in self.queue:
            if packet.size > available_bandwidth:
                break
            self.queue.remove(packet)
            available_bandwidth -= packet.size
            tp += 1
            # print(f' At {time}, # {tp} packet sent, packet size: {self.qsize}')
        self.wasted_bandwidth += available_bandwidth/self.packet_size
        # print(f'{available_bandwidth} of channel wasted!')
