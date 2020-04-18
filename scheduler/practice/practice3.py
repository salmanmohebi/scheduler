import simpy
from scheduler.utils.traffic_generator import *
from scheduler.utils.traffic_models import *

env = simpy.Environment()
client = Client(env)
bt = bursty_traffic(10, 5)
TrafficGenerator(
            env,
            adist=lambda: next(bt),
            sdist=lambda: 100,
            out=Server(env, name='srv1', bandwidth=2 ** 8, out=client)
        )
env.run(100)
