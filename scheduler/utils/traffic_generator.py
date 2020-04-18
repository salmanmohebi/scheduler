"""
Some ideas come from: https://www.grotto-networking.com/DiscreteEventPython.html
"""
from simpy import Environment, Store


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
        # return f'Packet: {self.seq_no}'
        return f'Packet: {{no. {self.seq_no}, time: {self.time}, ' \
               f'size: {self.size}, src: {self.src}, dst: {self.dst}}}'


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
                 sdist=lambda: 2**8, out=None, start: float = 0, end: float = float('inf')):
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
            # print(f'{packet}, generated at {self.env.now}')

            self.seq_no = (self.seq_no + 1) % 2**10
            assert self.out
            self.out.put(packet)
            # wait for next packet
            yield self.env.timeout(self.adist())


class Server:
    """ Create the Server class to store the generated packets in the buffer
    and transmit them over the channel

    Args:
        env (simpy.Environment): simulation environment
        name (str): name or id of the server
        q_unit (str): queue size unit which can be either in packets or bytes
        max_qsize (int): maximum size of queue
        bandwidth (float): the bandwidth of channel to transmit
        out: the channel class with a put methods

    Return:
        traffic streams, that transmitted over the channel
    """

    def __init__(self, env: Environment, name: str = 'server', q_unit: str = 'packets',
                 max_qsize: int = 5000, bandwidth: float = None, out=None):

        if q_unit not in ['packets', 'bytes']:
            raise ValueError('q_size_uint must be either `packets` or `bytes`')

        self.env = env
        self.name = name
        self.max_size = self.free = max_qsize
        self.q_unit = q_unit
        self.queue = Store(env, capacity=max_qsize)
        self.dropped_count = self.dropped_size = 0
        self.bandwidth = bandwidth

        # allocation parameters
        self.dti_duration = 100
        self.start = 0
        self.duration = self.dti_duration
        self.period = self.dti_duration + 1
        self.out = out
        self.env.process(self.send())

    def send(self):
        """ Transmit the packets over the channel using the channels put function """

        while True:
            dti_end = self.env.now + self.dti_duration

            # wait until starting time
            assert self.start >= 0
            yield self.env.timeout(self.start)
            while self.env.now < dti_end:

                s_time = self.env.now
                while self.env.now - s_time < self.duration:

                    pkt = yield self.queue.get()
                    self.free += pkt.size

                    print(f'{pkt}, send at {self.env.now}')
                    # wait until the current packet transmitted
                    assert pkt.size * 8 / self.bandwidth > 0
                    yield self.env.timeout(pkt.size * 8 / self.bandwidth)
                    self.out.put(pkt)

                if self.env.now + self.period <= dti_end:
                    # wait for next period
                    assert self.period - self.duration > 0
                    yield self.env.timeout(self.period - self.duration)
                else:
                    # wait until the end of dti after last period
                    yield self.env.timeout(dti_end - self.env.now)

    def put(self, pkt):
        """ Store the received traffic from the higher layer in the buffer """
        if self.q_unit == 'bytes' and self.free >= pkt.size:
            self.free -= pkt.size
            return self.queue.put(pkt)
        elif self.q_unit == 'packets' and self.free > 0:
            self.free -= 1
            return self.queue.put(pkt)
        else:
            self.dropped_count += 1
            self.dropped_size += pkt.size
            return


class Client:
    """ Client class which receives the traffics from channel
     and can applied some analysis on like as calculating
     the average delay

     Args:
        env (simpy.Environment): simulation environment
        name (str): name or id of the server
     """

    def __init__(self, env: Environment, name: str = 'receiver'):
        self.env = env
        self.name = name

    def put(self, pkt):
        """ Receives traffics from the channel """
        # print(f'{pkt}, received at {self.env.now}')
