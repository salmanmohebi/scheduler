import numpy as np


def cbr_traffic(const):
    return const


def bursty_traffic(batch_size, period):
    while True:
        for _ in range(batch_size):
            yield 0
        yield period


def poisson_traffic(lam, size=1):
    return np.random.poisson(lam, size)
