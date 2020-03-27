import simpy


class Car(object):
    def __init__(self, env, name):
        self.env = env
        self.name = name
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        while True:
            print(f'Start parking car {self.name} and charging at {self.env.now}')
            charge_duration = 5+self.name
            # We yield the process that process() returns
            # to wait for it to finish
            yield self.env.process(self.charge(charge_duration))
            # The charge process has finished and
            # we can start driving again.
            print(f'Start driving {self.name} at {self.env.now}')
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)


env = simpy.Environment()
car1 = Car(env, 1)
car2 = Car(env, 2)
car3 = Car(env, 3)
env.run(until=15)
