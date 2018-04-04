from agent import SmartAgent, RandomAgent, MaxAgent, OptionalAgent, MCTSAgent, Node
from simulator import play_game
import argparse
import sys
import threading

agent_list = {
    "smart": SmartAgent,
    "random": RandomAgent,
    "max": MaxAgent,
    "option": OptionalAgent,
    "mcts": MCTSAgent
}


def generate_agent(name):
    if name in agent_list.keys():
        return agent_list[name]
    else:
        raise NotImplementedError


def main():
    parser = argparse.ArgumentParser("python main.py")
    parser.add_argument("-p1", dest="p1")
    parser.add_argument("-p2", dest="p2")
    parser.add_argument("-k", dest="k", type=int)
    parser.add_argument("-mod", dest="mod", type=int)
    parser.add_argument("-num", dest="num", type=int)
    parser.add_argument("debug")
    args = parser.parse_args()

    agent1 = generate_agent(args.p1)(args.k, args.mod)
    agent2 = generate_agent(args.p2)(args.k, args.mod)
    if args.debug is None:
        debug = False
    else:
        debug = True

    if args.num is None:
        play_game(agent1, agent2, args.k, args.mod, debug)
    else:
        num = int(args.num)
        win1, step1 = 0, 0
        win2, step2 = 0, 0
        draw = 0

        for a in range(0, num):
            if a % 1 == 0 and debug:
                print("%d games done... %d:%d:%d" % (a, win1, win2, draw))
            result, step = play_game(agent1, agent2, args.k, args.mod, False)
            # print(result, step)
            if result == 0:
                draw += 1
            elif result == 1:
                win1 += 1
                step1 += step
            else:
                win2 += 1
                step2 += step

        print("%s vs %s, %d : %d, draw %d, step1 %d, step2 %d" % (args.p1, args.p2, win1, win2, draw, step1, step2))


if __name__ == "__main__":
    sys.setrecursionlimit(10 ** 5)
    threading.stack_size(200000000)
    thread = threading.Thread(target=main)
    thread.start()
    thread.join()
