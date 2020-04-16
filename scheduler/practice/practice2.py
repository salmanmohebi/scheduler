import matplotlib.pyplot as plt
import scipy
import seaborn as sns
import numpy as np


def cutter(str):
    return float(str[1:-2])/(10**6)


with open('output1.txt') as f:
    read_data = f.read()
    data = list(map(int, read_data.split()))
    # data = [x - data[i - 1] for i, x in enumerate(data)][1:]
    print(max(data))
    # create some randomly ddistributed data:
    # data = np.random.randn(10000)

    # sort the data:
    data_sorted = np.sort(data)

    # calculate the proportional values of samples
    p = 1. * np.arange(len(data)) / (len(data) - 1)

    # plot the sorted data:
    # fig = plt.figure()
    # ax1 = fig.add_subplot(121)
    # ax1.plot(p, data_sorted)
    # ax1.set_xlabel('$p$')
    # ax1.set_ylabel('$x$')

    # ax2 = fig.add_subplot(122)
    plt.plot(data_sorted, p)
    # plt.xlim(-0.1, 20)
    # plt.set_xlabel('$x$')
    # plt.set_ylabel('$p$')
    plt.show()
    # Choose how many bins you want here
    # num_bins = 2
    #
    # # Use the histogram function to bin the data
    # counts, bin_edges = np.histogram(data, bins=num_bins)
    #
    # # Now find the cdf
    # cdf = np.cumsum(counts)
    #
    # # And finally plot the cdf
    # plt.plot(bin_edges[1:], cdf)
    #
    # plt.show()

