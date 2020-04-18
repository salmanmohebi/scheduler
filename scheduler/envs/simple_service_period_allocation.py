import simpy
import numpy as np
from gym import spaces, Env

from scheduler.utils.traffic_generator import *
from scheduler.utils.traffic_models import *


class SimpleServicePeriodAllocationV0(Env):
    def __init__(self):
        self.env = simpy.Environment()  # simpy environment
        self.number_of_stations = 4
        self.stations = list()

        # records statistics
        self.dropped_pkts, self.wasted_resources, self.outdated_pkts, \
        self.successful_transmission = np.zeros((4, self.number_of_stations))

    def reset(self):
        self._initiate_env()

    def step(self, action):
        dti_duration = 50
        self.stations[0].start = 5
        self.stations[0].duration = 3
        self.stations[0].period = 10
        self.stations[0].dti_duration = dti_duration
        # self.stations[1].start = 5
        # self.stations[1].duration = 5
        # self.stations[1].period = dti_duration + 1
        # self.stations[2].start = 15
        # self.stations[2].duration = 3
        # self.stations[2].period = 10

        self.env.run(until=dti_duration)
        print('-----------------------')
        self.stations[0].start = 0
        self.stations[0].duration = 5
        self.stations[0].period = 15
        self.stations[0].dti_duration = dti_duration
        self.env.run(until=2*dti_duration)
        print('hi')

    def seed(self, seed=None):
        pass

    def render(self, mode='human'):
        pass

    def _initiate_env(self):
        client = Client(self.env)
        # srv1 = Server(self.env, name='srv1', bandwidth=2 ** 11, out=client)
        srv2 = Server(self.env, name='srv2', bandwidth=2 ** 11, out=client)
        # srv3 = Server(self.env, name='srv3', bandwidth=2 ** 11, out=client)
        # self.stations.extend([srv1, srv2, srv3])
        self.stations.append(srv2)

        # tr1 = TrafficGenerator(self.env, src='srv1', adist=lambda: 10,
        #                        sdist=lambda: 2**8, out=srv1)
        bt = bursty_traffic(5, 10)
        tr2 = TrafficGenerator(self.env, src='srv2', adist=lambda: next(bt),
                               sdist=lambda: 2**8, out=srv2)
        # tr3 = TrafficGenerator(self.env, src='srv3', adist=lambda: poisson_traffic(15),
        #                        sdist=lambda: 2**8, out=srv3)
