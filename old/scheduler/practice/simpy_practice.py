import simpy

buffer = [0, 0]


def generate(env, idx, tick):
    global buffer
    while True:
        if buffer[idx] < 30:
            new = min(1, 30 - buffer[idx])
            buffer[idx] += new
            print(f' {idx} in {env.now}, {new} new added, size: {buffer[idx]}')
        yield env.timeout(tick)


def transmit(env, idx, tick):
    global buffer
    while True:
        sent = 0
        # while buffer[idx] > 0 and sent < 4:
        buffer[idx] -= 1
        sent += 1
        # yield env.timeout(0.5)
        print(f' {idx} in {env.now}, {1} transmit, size: {buffer[idx]}')
        yield env.timeout(tick)


env = simpy.Environment()
env.process(generate(env, 0, 4))
env.process(transmit(env, 0, 10))
env.process(generate(env, 1, 4))
env.process(transmit(env, 1, 10))
env.run(until=100)
