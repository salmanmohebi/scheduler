import numpy as np
from gym import Env


TIME = None


class ServicePeriodAllocationV0(Env):
    metadata = {
        'render.modes': ['human', 'rgb_array']
    }

    def __init__(self, dti_duration, channel_bandwidth, channel_bit_loss_rate):
        self.dti_duration = dti_duration
        self.allocation_period = None
        self.allocation_duration = None

        self.channel_bandwidth = channel_bandwidth
        self.channel_bit_loss_rate = channel_bit_loss_rate
        self.cbr = None

    def reset(self):
        self.cbr = ConstantBitRateTraffic()
        self.cbr.update_queue(0)
        self.allocation_duration = np.random.randint(1, self.dti_duration//5)
        self.allocation_period = np.random.randint(
            self.allocation_duration, self.dti_duration - self.allocation_duration
        )

    def seed(self, seed=0):
        pass

    def step(self, action):
        pass

    def render(self, mode='human', close=False):
        pass


class Packet:
    def __init__(self, time):
        self.generated_time = time
        self.size = 256

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
        self.dropped_packets_overflow = 0
        self.dropped_packets_outdated = 0
        self.wasted_bandwidth = 0

    def generate_new_packets(self, time):
        number_of_packets = np.random.randint(1, self.maximum_generated_packet)
        for i, p in enumerate(range(number_of_packets)):
            if len(self.queue) < self.maximum_queue_length:
                self.queue.append(Packet(time))
                print(f'New packet added to queue, at {time}, the length of queue is: {len(self.queue)}')
            else:
                self.dropped_packets_overflow += number_of_packets - i
                print(f'Queue overflowed at {time}  and {number_of_packets - i} packets dropped')
                break

    def delete_outdated_packets(self, time):
        old_queue_size = len(self.queue)
        self.queue = [p for p in self.queue if p.age(time) <= self.delay_bound]
        self.dropped_packets_outdated += old_queue_size - len(self.queue)
        print(f' #{old_queue_size - len(self.queue)} outdated packets dropped')

    def update_queue(self, time):
        for t in range(self.last_packet_time, time, self.packet_generation_period):
            self.delete_outdated_packets(t)
            self.generate_new_packets(t)
            self.last_packet_time = t
        self.last_packet_time += self.packet_generation_period

    def transmit_traffic(self, duration, bandwidth, bit_error_rate=None):
        # TODO: Send data with probability of 1-bit_error_rate
        data_transmission_rate = bandwidth//duration
        for packet in self.queue:
            if packet.size > data_transmission_rate:
                break
            self.queue.remove(packet)
            data_transmission_rate -= packet.size
        # TODO: Calculate wasted_bandwidth based on packet size
        self.wasted_bandwidth += data_transmission_rate
        print(f'{data_transmission_rate} of channel wasted!')
