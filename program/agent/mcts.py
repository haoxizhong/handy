from .basic import BasicAgent
from utils import generate_from_action, generate_available_action, end
import random
import math


class Node:
    def __init__(self, s, depth):
        self.state = s
        self.next = []
        self.n = 0
        self.v = 0
        self.depth = depth

    def ucb(self, n):
        if self.n == 0:
            return 1e+20
        else:
            return - 1.0 * self.v / self.n + math.sqrt(math.log2(n) / self.n)

    def value(self):
        if self.n == 0:
            return 1e+20
        else:
            return 1.0 * self.v / self.n


class MCTSAgent(BasicAgent):
    def __init__(self, k, mod):
        super().__init__(k, mod)
        self.k = k
        self.mod = mod
        self.root = None
        self.se = set()

    def reinit(self):
        self.root = None
        self.se = set()

    def add_state(self, s):
        if self.mod == 2:
            self.se.add(s)

    def remove_state(self, s):
        if self.mod == 2:
            self.se.remove(s)

    def simulate(self, p):
        pse = set(list(self.se))
        if self.mod == 2:
            pse.add(p.state)

        depth = p.depth
        l1, r1, l2, r2, turn = p.state
        lose = False
        while not (end(l1, r1, l2, r2)) and depth <= self.k ** 2:
            action_list = generate_available_action(self.k, l1, r1, l2, r2, turn, pse, self.mod)
            if len(action_list) == 0:
                lose = True
                break
            op1, op2 = action_list[random.randint(0, len(action_list) - 1)]
            l1, r1, l2, r2, turn = generate_from_action(self.k, l1, r1, l2, r2, turn, op1, op2)
            depth += 1
            if self.mod == 2:
                pse.add((l1, r1, l2, r2, turn))

        if end(l1, r1, l2, r2) or lose:
            if turn == p.state[4]:
                return 0
            else:
                return 2
        else:
            return 1

    def expand(self, p):
        l1, r1, l2, r2, turn = p.state
        action_list = generate_available_action(self.k, l1, r1, l2, r2, turn, self.se, self.mod)
        p.next = []
        for op1, op2 in action_list:
            news = generate_from_action(self.k, l1, r1, l2, r2, turn, op1, op2)
            p.next.append(Node(news, p.depth + 1))

        result = self.simulate(p)
        # print(result)
        p.n += 1
        p.v += result

        return result

    def election(self, nowp):
        if nowp.n == 0 or end(nowp.state[0], nowp.state[1], nowp.state[2],
                              nowp.state[3]) or nowp.depth == self.k ** 4 or len(nowp.next) == 0:
            return 2 - self.expand(nowp)

        next_p = None
        for p in nowp.next:
            if next_p is None or next_p.ucb(nowp.n) < p.ucb(nowp.n):
                next_p = p

        if next_p is None:
            print("what")

        self.add_state(nowp.state)
        result = self.election(next_p)
        nowp.n += 1
        nowp.v += result
        self.remove_state(nowp.state)

        return 2 - result

    def check(self, l1, r1, l2, r2, turn, action_list):
        for a in range(0, len(action_list)):
            news = generate_from_action(self.k, l1, r1, l2, r2, turn, action_list[a][0], action_list[a][1])
            if news != self.root.next[a].state:
                raise NotImplementedError

    def next_step(self, l1, r1, l2, r2, action_list):
        if self.root is None:
            if l1 + r1 + l2 + r2 == 4:
                self.add_state((1, 1, 1, 1, 0))
                self.root = Node((1, 1, 1, 1, 0), 0)
            else:
                self.add_state((1, 1, 1, 1, 0))
                self.add_state((l2, r2, l1, r1, 1))
                self.root = Node((l2, r2, l1, r1, 1), 1)
                l1, l2 = l2, l1
                r1, r2 = r2, r1
        else:
            turn = 1 - self.root.state[4]
            if turn == 1:
                l1, l2 = l2, l1
                r1, r2 = r2, r1
            for node in self.root.next:
                if node.state == (l1, r1, l2, r2, turn):
                    self.root = node
                    break
            self.add_state(self.root.state)
        # print(self.root.state)

        iteration_time = self.k ** 2
        for a in range(0, iteration_time):
            self.election(self.root)
        self.check(l1, r1, l2, r2, self.root.state[4], action_list)

        next_p = None
        cnt = 0
        idx = 0
        for p in self.root.next:
            if next_p is None or p.value() < next_p.value():
                next_p = p
                idx = cnt
            cnt += 1
        self.root = next_p

        self.add_state(self.root.state)

        return idx
