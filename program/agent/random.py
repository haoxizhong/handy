from .basic import BasicAgent
from utils import generate_from_action
import random


class RandomAgent(BasicAgent):
    def __init__(self, k, mod):
        super().__init__(k, mod)
        self.k = k

    def reinit(self):
        pass

    def next_step(self, l1, r1, l2, r2, action_list):
        return random.randint(0, len(action_list) - 1)
