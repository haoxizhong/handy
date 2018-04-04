import time


def print_time():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def generate_from_action(k, l1, r1, l2, r2, turn, op1, op2):
    if turn == 0:
        h = [[l1, r1], [l2, r2]]
        h[0][op1] = (h[0][op1] + h[1][op2]) % k
    else:
        h = [[l1, r1], [l2, r2]]
        h[1][op1] = (h[1][op1] + h[0][op2]) % k

    return h[0][0], h[0][1], h[1][0], h[1][1], 1 - turn


def end(l1, r1, l2, r2):
    if (l1 == 0 and r1 == 0) or (l2 == 0 and r2 == 0):
        return True
    return False


def generate_available_action(k, l1, r1, l2, r2, turn, se, mod):
    # if l1==1 and r1==1 and l2==9 and r2==5 and turn==0:
    #    print("gg")
    if turn == 0:
        h = [[l1, r1], [l2, r2]]
    else:
        h = [[l2, r2], [l1, r1]]

    action_list = []

    for op1 in range(0, 2):
        for op2 in range(0, 2):
            if h[0][op1] != 0 and h[1][op2] != 0:
                r = [[h[0][0], h[0][1]], [h[1][0], h[1][1]]]
                r[0][op1] = (r[0][op1] + r[1][op2]) % k
                l1, r1, l2, r2 = r[0][0], r[0][1], r[1][0], r[1][1]
                if turn == 1:
                    l1, l2 = l2, l1
                    r2, r1 = r1, r2

                news = (l1, r1, l2, r2, 1 - turn)
                if mod == 2 and news in se:
                    pass
                else:
                    action_list.append((op1, op2))

    return action_list
