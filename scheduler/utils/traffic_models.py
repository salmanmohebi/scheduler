import numpy as np


def cbr_traffic(const: float):
    return const


def bursty_traffic(batch_size: int, period: float):
    while True:
        for _ in range(batch_size):
            yield 0
        yield period


def poisson_traffic(lam: float, size: int = 1):
    return np.random.poisson(lam, size)


def gaussian_traffic(mu: float, sigma: float, size: int = 1):
    return np.random.normal(loc=mu, scale=sigma, size=size)


def traffic2(data_rate: float, packet_size):
    pass
