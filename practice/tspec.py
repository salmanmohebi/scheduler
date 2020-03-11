import random

TIME = 0


class Packet:
    def __init__(self, number=0, time=0, size=4):
        self.number = number
        self.time = time
        self.size = random.randint(2, size)

    @property
    def age(self):
        return TIME - self.time

    def __str__(self):
        return f'TIME: {TIME}: Packet with number: {self.number}, created at time: {self.time}'


class Packets:
    def __init__(self, period):
        self.period = period
        self.number = 0
        self.time = 0
        self.queue = list()

    def __next__(self):
        return self.next()

    def next(self):
        while self.time <= TIME:
            self.queue.append(Packet(self.number, self.time))
            self.number += 1
            self.time += self.period
            # print(f'TIME: {TIME} : {[(p.number, p.time) for p in self.queue]} | the {(self.queue[0].number, self.queue[0].time)} sent')
            # print(f' In {TIME}, packet {self.queue[0].number} that was generated in {self.queue[0].time} sent')
        return self.queue


if __name__ == '__main__':
    total_drops, total_waste = 0, 0
    allocation_period = 12
    allocation_duration = 6
    delay_bound = 10
    packet = Packets(period=10)
    while TIME < 10000:
        # print(TIME, packet.time, len(packet.queue))
        queue = next(packet)

        # Remove out-dated packet
        d = queue[0].age
        while d > delay_bound:
            q = queue.pop(0)
            d = q.age
            print(f' ->In {TIME}, packet {q.number} that was generated in {q.time} dropped')
            total_drops += q.size
            if allocation_period > 2:
                allocation_period -= 1

        # Sent the packets
        d = allocation_duration
        while d > 0 and len(queue) > 0:
            if queue[0].size > d:
                queue[0].size -= d
                # print(f' In {TIME}, {d} Bytes of packet {queue[0].number} that was generated in {queue[0].time} sent')
                break
            else:
                q = queue.pop(0)
                d = d - q.size
                print(f' ->In {TIME}, {q.size} Bytes of packet {q.number} that was generated in {q.time} sent || duration is {allocation_duration}, period is {allocation_period}')
                if len(queue) == 0 and d > 0:
                    print(f'{d} amount of channel wasted!!!')
                    total_waste += d
                    # if allocation_duration > 2:
                    #     allocation_duration -= 1
                    break

        TIME += allocation_period

    print(f'TOTAL WASTE: {total_waste}, TOTAL DROPS: {total_drops}')
