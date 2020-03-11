import numpy as np

p = 0.8

H = [1, 2]
M = [1, 2, 3]
N = [1, 2, 3, 4]
l = len(H) * len(M) * len(N)

A = np.zeros(l, l)
for h in H:
    for m in M:
        for n in N:
            if h < 0:
                A[h+m+n, h+m+n] = 1
            else:
                A[h+m+n, h+m+n] = 1 - p
                if m > 1:
                    A[h+m+n, ]


