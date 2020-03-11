import numpy as np

import time
start_time = time.time()
a = 25000
A = np.random.random((a, a))
print('start...')
np.matmul(A, A)
print('end...')
print("--- %s seconds ---" % (time.time() - start_time))
