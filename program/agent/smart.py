import pdb
import queue
from .basic import BasicAgent
from utils import generate_from_action


class SmartAgent(BasicAgent):
    def get(self, a, b):
        return (a + b) % self.k

    def add(self, a, b):
        self.pre[b].append(a)
        self.next[a].append(b)
        self.out_cnt[a] += 1
        self.in_cnt[b] += 1

    def reform_state(self, l0, r0, l1, r1, turn):
        if l0 > r0:
            l0, r0 = r0, l0
        if l1 > r1:
            l1, r1 = r1, l1
        return l0, r0, l1, r1, turn

    def generate_next(self, l0, r0, l1, r1, turn):
        if turn == 0:
            if l0 != 0 and l1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(self.get(l0, l1), r0, l1, r1, 1))
            if l0 != 0 and r1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(self.get(l0, r1), r0, l1, r1, 1))
            if r0 != 0 and l1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(l0, self.get(r0, l1), l1, r1, 1))
            if r0 != 0 and r1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(l0, self.get(r0, r1), l1, r1, 1))
        else:
            if l0 != 0 and l1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(l0, r0, self.get(l1, l0), r1, 0))
            if r0 != 0 and l1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(l0, r0, self.get(l1, r0), r1, 0))
            if l0 != 0 and r1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(l0, r0, l1, self.get(r1, l0), 0))
            if r0 != 0 and r1 != 0:
                self.add(self.reform_state(l0, r0, l1, r1, turn), self.reform_state(l0, r0, l1, self.get(r1, r0), 0))

    def format_array(self, l):
        l.sort()
        z = []
        for x in l:
            if len(z) == 0 or z[-1] != x:
                z.append(x)
        return z

    def t(self, l0, r0, l1, r1, turn):
        x = (l0, r0, l1, r1, turn)
        print("f", self.f[x])
        print("next", self.next[x])
        print("pre", self.pre[x])

    def __init__(self, k, mod):
        super().__init__(k, mod)
        self.f = {}
        self.next = {}
        self.pre = {}
        self.in_cnt = {}
        self.out_cnt = {}
        self.k = k

        for a in range(0, k):
            for b in range(a, k):
                for c in range(0, k):
                    for d in range(c, k):
                        for e in range(0, 2):
                            self.f[(a, b, c, d, e)] = None
                            self.pre[(a, b, c, d, e)] = []
                            self.next[(a, b, c, d, e)] = []
                            self.in_cnt[(a, b, c, d, e)] = 0
                            self.out_cnt[(a, b, c, d, e)] = 0

        for a in range(0, k):
            for b in range(a, k):
                for c in range(0, k):
                    for d in range(c, k):
                        for e in range(0, 2):
                            self.generate_next(a, b, c, d, e)

        for a in range(0, k):
            for b in range(a, k):
                for c in range(0, k):
                    for d in range(c, k):
                        for e in range(0, 2):
                            x = (a, b, c, d, e)
                            self.next[x] = self.format_array(self.next[x])
                            self.pre[x] = self.format_array(self.pre[x])
                            self.in_cnt[x] = len(self.pre[x])
                            self.out_cnt[x] = len(self.next[x])

        q = queue.Queue()

        for a in range(0, k):
            for b in range(a, k):
                for c in range(0, k):
                    for d in range(c, k):
                        for e in range(0, 2):
                            if a + b + c + d != 0:
                                if a == 0 and b == 0 and e == 1:
                                    self.f[(a, b, c, d, e)] = False
                                    q.put((a, b, c, d, e))
                                if c == 0 and d == 0 and e == 0:
                                    self.f[(a, b, c, d, e)] = False
                                    q.put((a, b, c, d, e))

        # file_out = open("result.txt", "w")

        while q.qsize() != 0:
            now = q.get()
            # print(now, f[now], file=file_out)
            for x in self.pre[now]:
                self.out_cnt[x] -= 1
                if self.f[x] is None and (self.out_cnt[x] == 0 or self.f[now] == False):
                    if self.f[now] == False:
                        self.f[x] = True
                    else:
                        self.f[x] = False
                    q.put(x)

        # pdb.set_trace()

    def reinit(self):
        pass

    def next_step(self, l1, r1, l2, r2, action_list):
        s = self.reform_state(l1, r1, l2, r2, 0)

        lose_s = None
        none_s = None
        win_s = None

        for idx in range(0, len(action_list)):
            op1, op2 = action_list[idx]
            ns = generate_from_action(self.k, l1, r1, l2, r2, 0, op1, op2)
            nexts = self.reform_state(ns[0], ns[1], ns[2], ns[3], ns[4])

            if self.f[nexts] is None:
                none_s = idx
            elif self.f[nexts] is False:
                lose_s = idx
            else:
                win_s = idx

        if not (lose_s is None):
            return lose_s
        elif not (none_s is None):
            return none_s
        else:
            return win_s


if __name__ == "__main__":
    pass
