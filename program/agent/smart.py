import pdb
import queue
from .basic import BasicAgent
from utils import generate_from_action, generate_available_action, end
import random


class SmartAgent2(BasicAgent):
    def generate_next(self, l1, r1, l2, r2, turn):
        action_list = generate_available_action(self.k, l1, r1, l2, r2, turn, set(), self.mod)
        for op1, op2 in action_list:
            news = generate_from_action(self.k, l1, r1, l2, r2, turn, op1, op2)
            self.next[(l1, r1, l2, r2, turn)].append(news)
            self.pre[news].append((l1, r1, l2, r2, turn))

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

    def dfs(self, s, dic, dep):
        if s in self.next_cnt.keys():
            return self.next_cnt[s]

        dic[s] = dep

        cnt = 0
        ns = None
        for nexts in self.next[s]:
            if self.f[nexts] is None and not (nexts in dic.keys()):
                cnt += 1
                ns = nexts

        if cnt == 0:
            result = [0, 0]
            for nexts in self.next[s]:
                if self.f[nexts] is None:
                    if dic[nexts] % 2 == dep % 2:
                        result[1] += 1
                    else:
                        result[0] += 1

            able = [False, False]
            able[0] = result[0] > 0 or result[1] > 1
            able[1] = result[1] > 0
            self.next_cnt[s] = able
            return able
        elif cnt == 1:
            able = self.dfs(ns, dic, dep + 1)
            able[0], able[1] = able[1], able[0]
            self.next_cnt[s] = able
            return able
        else:
            return [False, False]

    def __init__(self, k, mod):
        super().__init__(k, mod)
        self.f = {}
        self.next = {}
        self.pre = {}
        self.in_cnt = {}
        self.out_cnt = {}
        self.next_cnt = {}
        self.k = k
        self.mod = mod

        for a in range(0, k):
            for b in range(0, k):
                for c in range(0, k):
                    for d in range(0, k):
                        for e in range(0, 2):
                            self.f[(a, b, c, d, e)] = None
                            self.pre[(a, b, c, d, e)] = []
                            self.next[(a, b, c, d, e)] = []
                            self.in_cnt[(a, b, c, d, e)] = 0
                            self.out_cnt[(a, b, c, d, e)] = 0

        for a in range(0, k):
            for b in range(0, k):
                for c in range(0, k):
                    for d in range(0, k):
                        for e in range(0, 2):
                            self.generate_next(a, b, c, d, e)

        for a in range(0, k):
            for b in range(0, k):
                for c in range(0, k):
                    for d in range(0, k):
                        for e in range(0, 2):
                            x = (a, b, c, d, e)
                            self.next[x] = self.format_array(self.next[x])
                            self.pre[x] = self.format_array(self.pre[x])
                            self.in_cnt[x] = len(self.pre[x])
                            self.out_cnt[x] = len(self.next[x])

        q = queue.Queue()

        for a in range(0, k):
            for b in range(0, k):
                for c in range(0, k):
                    for d in range(0, k):
                        for e in range(0, 2):
                            if a + b + c + d != 0:
                                if a == 0 and b == 0 and e == 1:
                                    self.f[(a, b, c, d, e)] = False
                                    q.put((a, b, c, d, e))
                                if c == 0 and d == 0 and e == 0:
                                    self.f[(a, b, c, d, e)] = False
                                    q.put((a, b, c, d, e))

        while q.qsize() != 0:
            now = q.get()
            for x in self.pre[now]:
                self.out_cnt[x] -= 1
                if self.f[x] is None and (self.out_cnt[x] == 0 or self.f[now] == False):
                    if self.f[now] == False:
                        self.f[x] = True
                    else:
                        self.f[x] = False
                    q.put(x)

        for a in range(0, k):
            for b in range(0, k):
                for c in range(0, k):
                    for d in range(0, k):
                        for e in range(0, 2):
                            s = (a, b, c, d, e)
                            if self.f[s] is None and not (s in self.next_cnt.keys()):
                                self.dfs(s, {}, 0)

    def reinit(self):
        pass

    def next_step(self, l1, r1, l2, r2, action_list):
        s = (l1, r1, l2, r2, 0)

        lose_s = []
        none_s0 = []
        none_s1 = []
        win_s = []

        for idx in range(0, len(action_list)):
            op1, op2 = action_list[idx]
            nexts = generate_from_action(self.k, l1, r1, l2, r2, 0, op1, op2)

            if self.f[nexts] is None:
                if nexts in self.next_cnt.keys():
                    if self.next_cnt[nexts][0]:
                        none_s0.append(idx)
                    else:
                        none_s1.append(idx)
                else:
                    none_s1.append(idx)
            elif self.f[nexts] is False:
                lose_s.append(idx)
            else:
                win_s.append(idx)

        if len(lose_s) > 0:
            return lose_s[random.randint(0, len(lose_s) - 1)]
        elif len(none_s0) > 0:
            return none_s0[random.randint(0, len(none_s0) - 1)]
        elif len(none_s1) > 0:
            return none_s1[random.randint(0, len(none_s1) - 1)]
        else:
            return win_s[random.randint(0, len(win_s) - 1)]


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
        self.k = k
        self.mod = mod
        if mod == 2:
            self.agent = SmartAgent2(k, mod)
            return
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
        if self.mod == 2:
            return self.agent.next_step(l1, r1, l2, r2, action_list)
        s = self.reform_state(l1, r1, l2, r2, 0)

        lose_s = []
        none_s = []
        win_s = []

        for idx in range(0, len(action_list)):
            op1, op2 = action_list[idx]
            ns = generate_from_action(self.k, l1, r1, l2, r2, 0, op1, op2)
            nexts = self.reform_state(ns[0], ns[1], ns[2], ns[3], ns[4])

            if self.f[nexts] is None:
                none_s.append(idx)
            elif self.f[nexts] is False:
                lose_s.append(idx)
            else:
                win_s.append(idx)

        if len(lose_s) > 0:
            return lose_s[random.randint(0, len(lose_s) - 1)]
        elif len(none_s) > 0:
            return none_s[random.randint(0, len(none_s) - 1)]
        else:
            return win_s[random.randint(0, len(win_s) - 1)]


if __name__ == "__main__":
    pass
