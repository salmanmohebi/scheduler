import simpy

buffer = 0


def generate(env, tick):
    global buffer
    while True:
        if buffer < 30:
            new = min(4, 30 - buffer)
            buffer += new
            print(f'In {env.now}, {new} new added, size: {buffer}')
        yield env.timeout(tick)


def transmit(env, tick):
    global buffer
    while True:
        sent = 0
        while buffer > 0 and sent < 4:
            buffer -= 1
            sent += 1
            yield env.timeout(0.5)
            print(f'In {env.now}, {1} transmit, size: {buffer}')
        yield env.timeout(tick)


env = simpy.Environment()
env.process(generate(env, 4))
env.process(transmit(env, 10))
env.run(until=100)
