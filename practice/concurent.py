from threading import Thread, Lock
import time
import random

queue = 0
lock = Lock()


class ProducerThread(Thread):
    def run(self):
        # nums = range(5)
        p = 10
        global queue
        for t in range(0, 100, p):
            # num = random.choice(nums)
            lock.acquire()
            queue += 4
            print(f'Produced in {t}, length {queue}')
            lock.release()
            time.sleep(random.random(1, p))


class ConsumerThread(Thread):
    def run(self):
        p = 10
        global queue
        for t in range(5, 100, p):
            lock.acquire()
            if queue > 0:
                queue -= 1
                print(f'----Consumed in {t}, length {queue}')
            lock.release()
            time.sleep(random.random(1, p))


ProducerThread().start()
ConsumerThread().start()
