import numpy as np
from gym import spaces, Env


# TODO: choose a more meaningful class name
class Ieee80211AdV0(Env):
    metadata = {
        'render.modes': ['human', 'rgb_array']
    }

    def __init__(self):
        pass

    def reset(self):
        pass

    def seed(self, seed=0):
        pass

    def step(self, action):
        pass

    def render(self, mode='human', close=False):
        pass

    def _generate_traffic(self):
        for u, qi in enumerate(self.qi):
            if self.tti == self.tti_next_pkt[u]:
                buffer_gaps = np.where(self.s[u, :] == 0)[0]  # Find slots for packets in the queue.
                if buffer_gaps.size == 0:  # Large negative rwd unnecessary b/c rwd is already max due to full buffer.
                    print(f"Buffer overflow. Disregarding new GBR (Conversational Voice) packet for UE {u}.")
                    g = None
                else:
                    g = buffer_gaps[0]  # First available slot in buffer
                    self.e[u, g] = 0  # Set the age of this new packet to 0

                if np.array_equal(qi, [0, 0, 0, 1]):  # 3: GBR (Conversational Voice)
                    if buffer_gaps.size > 0:
                        self.s[u, g] = 584
                    self.tti_next_pkt[u] = self.tti + 20
                elif np.array_equal(qi, [0, 0, 1, 0]):  # 2: GBR (Conversational Video)
                    # TODO: Use perhaps a more complex video traffic model such as the Markov-modulated Gamma model.
                    if buffer_gaps.size > 0:
                        self.s[u, g] = 41250
                    self.tti_next_pkt[u] = self.tti + 33
                elif np.array_equal(qi, [0, 1, 0, 0]):  # 1: Delay Critical GBR
                    if buffer_gaps.size > 0:
                        self.s[u, g] = 200
                    self.tti_next_pkt[u] = self.tti + 20
                elif np.array_equal(qi, [1, 0, 0, 0]):  # 0: Non-GBR
                    # Inspired by: https://www.nsnam.org/docs/models/html/applications.html?highlight=traffic%20model
                    if buffer_gaps.size > 0:
                        self.s[u, g] = min(max(1, np.random.geometric(1 / 20000)), self.max_pkt_size_bits)
                    self.tti_next_pkt[u] = self.tti + np.random.geometric(1 / self.it)

                if buffer_gaps.size > 0:
                    assert 1 <= self.s[u, g] <= self.max_pkt_size_bits, f"Packet size {self.s[u, g]} out of range."
