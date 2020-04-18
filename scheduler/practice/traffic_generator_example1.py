import simpy

from scheduler.utils.traffic_generator import *
from scheduler.utils.traffic_models import *

if __name__ == '__main__':
    env = simpy.Environment()
    client = Client(env)
    server = Server(env, name='sender', bandwidth=2**11, out=client)
    bt = bursty_traffic(2, 1)
    tr = TrafficGenerator(env, adist=lambda: next(bt),
                          sdist=lambda: 2**8, out=server)
    server.duration, server.period = 6, 12
    env.run(30)
    print(server.free, server.max_size, server.dropped_size, server.dropped_count)
