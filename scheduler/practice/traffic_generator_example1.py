import simpy

from scheduler.utils.traffic_generator import *

if __name__ == '__main__':
    env = simpy.Environment()
    client = Client(env)
    server = Server(env, name='sender', bandwidth=2**8, out=client)
    tr = TrafficGenerator(env, adist=lambda: 2,
                          sdist=lambda: 100, out=server)

    env.run(2**9)
    print(server.free, server.max_size, server.dropped_size, server.dropped_count)
