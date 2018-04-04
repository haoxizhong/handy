from .basic import BasicAgent
from utils import generate_from_action
import random


class MaxAgent(BasicAgent):
    def __init__(self, k, mod):
        super().__init__(k, mod)
        self.k = k

    def reinit(self):
        pass

    def next_step(self, l1, r1, l2, r2, action_list):
        result_sum = -1000
        sum_k = []
        for a in range(0, len(action_list)):
            op1, op2 = action_list[a]
            l1, r1, l2, r2, _ = generate_from_action(self.k, l1, r1, l2, r2, 0, op1, op2)
            if l1 == 0:
                l1 = self.k
            if r1 == 0:
                r1 = self.k
            if l1 + r1 > result_sum:
                result_sum = l1 + r1
            sum_k.append(l1 + r1)

        result = []
        for a in range(0, len(sum_k)):
            if sum_k[a] == result_sum:
                result.append(a)

        return result[random.randint(0, len(result) - 1)]
