import time
import numpy as np
from math import gcd
from functools import reduce


print('Start...')

Tin = 4 #20
epsilon = 0

Dqos = 5#50
p = 0.8
Tbi = 20# 103

B_list = [1, 2, 4, 6]
Tbhi_list = [5, 10, 20, 30]
Tabp_list = list(range(1, 50))


b = B_list[0]
Tbhi = Tbhi_list[0]
Tabp = Tabp_list[0]

N = (Tbi - Tbhi) // Tabp + 1

Tn = Tabp
Tnl = Tbhi + (Tbi - Tbhi) % Tabp


def get_gcd(list):
    x = reduce(gcd, list)
    return x


tau = get_gcd([Tin, Tn, Tnl])

tin = Tin//tau
tn = Tn//tau

d = (Dqos - epsilon) // tau

H = list(range(-tin, d))

M = list(range(1, 5))
Pj = [0, 0, 0, 1]

N1 = list(range(N))

l = len(H) * len(M) * N
A = C = np.zeros((len(H), len(M), len(N1), len(H), len(M), len(N1)))

# Calculating the transition matrix
for h in H:
    for m in range(4):
        for n in range(N):
            if h < 0:
                A[h, m, n, h, m, n] = 1
            else:
                A[h, m, n, h, m, n] = 1 - p
                if m > 1:
                    A[h, m, n, h, m-1, n] = p
                else:
                    for j in range(4):
                        A[h, m, n, h-tin, j, n] = p*Pj[j]
            # calculate the C matrix
            if h + tn < d:
                C[h, m, n, h+tn, m, (n+1) % N] = 1
            else:
                for j in range(4):
                    ahn = (h+tn-tin-d)//tin+1
                    A[h, m, n, h+tn-tin-ahn*tin, j, (n+1) % N] = Pj[j]

A = np.reshape(A, (l, l))
B = np.linalg.matrix_power(A, b)
C = np.reshape(C, (l, l))
tt = time.time()
print('Im here, before the multiply')
P = np.dot(B, C)
print(f'it took {time.time() - tt} to mul matrix')

# calculate the stationary distribution
evals, evecs = np.linalg.eig(P.T)
evec1 = evecs[:, np.isclose(evals, 1)]
evec1 = evec1[:, 0]
stationary = evec1 / evec1.sum()
stationary = stationary.real


ahn = (h+tn-tin-d)//(tn)+1
PRL = ((N*tin)/(4*tn*N))*sum


