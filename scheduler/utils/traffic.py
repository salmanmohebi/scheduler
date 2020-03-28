"""
Some ideas come from: https://www.grotto-networking.com/DiscreteEventPython.html
"""
from simpy import Environment


class Packet:
    """ The basic Packet class

    Args:
        time (float): the time which packet generated
        size (int): the size of packet in byte
        seq_no (int): packet sequence number
        src (str): address identifier of the packet source
        dst (str): address identifier of the packet destination

    Return:
        Packet: a packet object
    """

    def __init__(self, time: float = 0, size: int = 256,
                 seq_no: int = 0, src: str = 'src', dst: str = 'dst'):
        self.time = time
        self.size = size
        self.seq_no = seq_no
        self.src = src
        self.dst = dst

    def __str__(self):
        return f'Packet: no. {self.seq_no}, time: {self.time}, ' \
               f'size: {self.size}, src: {self.src}, dst: {self.dst}'


class TrafficGenerator:
    """ Generates different types of traffics, based on the parameters received

    Args:
        env (simpy.Environment): simulation environment
        tid (int): traffic stream identifier
        adist (function): a function that returns the distribution inter-arrival times between the packets
        sdist (function): a function that returns the distribution size of packets for traffic
        start (float): traffic starting time
        end (float): the time when traffic stream finish

    Return:
        traffic streams, that can save into the queue

    """

    def __init__(self, env: Environment, tid: int = 0, src='src', dst: str = 'dst', adist=lambda: 10,
                 sdist=lambda: 256, out=None, start: float = 0, end: float = float('inf')):
        self.env = env
        self.tid = tid
        self.src, self.dst = src, dst
        self.adist, self.sdist = adist, sdist
        self.start, self.end = start, end
        self.out = out
        self.seq_no = 0
        self.env.process(self.generate())

    def generate(self):
        """ Generate traffics based on received parameters """

        # wait for starting time
        yield self.env.timeout(self.start)
        while self.env.now < self.end:
            packet = Packet(
                time=self.env.now, size=self.sdist(),
                seq_no=self.seq_no, src=self.src, dst=self.dst
            )
            print(f'{packet} generated at {self.env.now}')

            self.seq_no = (self.seq_no + 1) % 2**10
            assert self.out
            self.out.put(packet)
            # wait for next packet
            yield self.env.timeout(self.adist())


class Mac:
    """ Create a class to store the generated packets

    Args:
        max_size (int): maximum size of buffer in bytes
    """

    def __init__(self, env: Environment, bandwidth: float = None, qlength: int = True,
                 qsize: bool = False, max_size: int = 5000, out=None):

        self.env = env
        self.bandwidth = bandwidth
        self.qlength = qlength
        self.qsize = qsize
        self.max_size = self.free = max_size
        self.buffer = simpy.Store(env, capacity=max_size)
        self.out = out
        self.dropped_count = self.dropped_size = 0
        self.env.process(self.transmit())

    def transmit(self):
        while True:
            pkt = yield self.buffer.get()
            self.free += pkt.size
            yield self.env.timeout(pkt.size * 8 / self.bandwidth)
            self.out.put(pkt)

    def put(self, pkt):
        if self.qsize and self.free >= pkt.size:
            self.free -= pkt.size
            return self.buffer.put(pkt)
        elif self.qlength and self.free > 0:
            self.free -= 1
            return self.buffer.put(pkt)
        else:
            self.dropped_count += 1
            self.dropped_size += pkt.size
            return


class Mac2:
    def __init__(self, env):
        self.env = env

    def put(self, pkt):
        print(f'{pkt}, received at {self.env.now}')


def func(n):
    while True:
        for _ in range(n):
            yield 0
        yield 1


if __name__ == '__main__':
    import simpy
    env = simpy.Environment()
    mac = Mac(env, bandwidth=2**10, out=Mac2(env))
    adist = func(1)
    tr = TrafficGenerator(env, adist=lambda: 1, out=mac)

    env.run(2**7)
    print(mac.free, mac.max_size, mac.dropped_size, mac.dropped_count)



