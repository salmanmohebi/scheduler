import numpy as np
import tensorflow as tf
from math import gcd
from functools import reduce


print('Start...')
Tin = 20
epsilon = 0

Dqos = 50
p = 0.8
Tbi = 103

B = [1, 2, 4, 6]
TBHI = [5, 10, 20, 30]
TABP = list(range(1, 50))

b = B[0]
Tbhi = TBHI[0]
Tabp = TABP[0]

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


# a = (h + tn - tin - d) // tin + 1

H = list(range(-tin, d))

M = list(range(4))
Pj = [0, 0, 0, 1]

N1 = list(range(N))

A = np.zeros((len(H), len(M), len(N1), len(H), len(M), len(N1)))
# print(A.shape)
# A[:, 3, :] = 1
# print(A.shape)

for h in H:
    for m in range(len(M)):
        for n in N1:
            if h < 0:
                A[h, m, n, h, m, n] = 1
            else:
                A[h, m, n, h, m, n] = 1 - p
                if m > 1:
                    A[h, m, n, h, m-1, n] = p
                else:
                    for j in M:
                        # TODO: remember the index of m started from zero
                        A[h, m, n, h-tin, j, n] = p*Pj[j]



print('Im here, before the multiply')
# KK = tf.linalg.matmul(A, A)
print('The things over now..;')
# print(type(KK))
# a12 = 1

mm = np.random.randint(1, 10, size=(4, 5, 3))
rr = tf.linalg.matmul(mm, mm)

print(f'Im done, here you are: {rr}')




