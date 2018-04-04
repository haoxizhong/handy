from .basic import BasicAgent
from utils import generate_from_action
import random


class OptionalAgent(BasicAgent):
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
            h = [[l1, r1], [l2, r2]]
            score = ((h[0][op1] + h[1][op2]) % 2 == self.k % 2) * 1000 + h[0][op1] * 10 + 10 - h[1][op2]
            if score > result_sum:
                result_sum = score
            sum_k.append(score)

        result = []
        for a in range(0, len(sum_k)):
            if sum_k[a] == result_sum:
                result.append(a)

        return result[random.randint(0, len(result) - 1)]
