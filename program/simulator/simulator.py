from utils import end, generate_available_action, generate_from_action
import pdb

debug_ = False

ma = {0: "左手", 1: "右手"}


def debug(inf):
    global debug_
    if debug_:
        print(inf)


def play_game(agent1, agent2, k, mod, deb):
    global debug_
    debug_ = deb

    debug("Game begin")

    debug("Agent1 initializing...")
    agent1.reinit()
    debug("Agent1 init done")

    debug("Agent2 initializing...")
    agent2.reinit()
    debug("Agent2 init done")

    l1, r1, l2, r2 = 1, 1, 1, 1
    turn = 0
    step = 0

    se = set()
    step_limit = k*k*k*k

    while not (end(l1, r1, l2, r2)) and step < step_limit:
        se.add((l1, r1, l2, r2, turn))

        action_list = generate_available_action(k, l1, r1, l2, r2, turn, se, mod)
        if len(action_list) == 0:
            break

        if turn == 0:
            action = agent1.next_step(l1, r1, l2, r2, action_list)
            l1, r1, l2, r2, _ = generate_from_action(k, l1, r1, l2, r2, 0, action_list[action][0],
                                                     action_list[action][1])
            #print(action_list)
        else:
            action = agent2.next_step(l2, r2, l1, r1, action_list)
            l2, r2, l1, r1, _ = generate_from_action(k, l2, r2, l1, r1, 0, action_list[action][0],
                                                     action_list[action][1])

        step = step + 1
        turn = 1 - turn

        debug("Step %d, Player %d use action (%s,%s), get state (%d,%d,%d,%d)" % (
            step, 2 - turn, ma[action_list[action][0]], ma[action_list[action][1]], l1, r1, l2, r2))

    if step >= step_limit:
        result = 0
        debug("Draw")
    elif turn == 0:
        result = 2
        debug("Agent 2 wins")
    else:
        result = 1
        debug("Agent 1 wins")

    return result, step
