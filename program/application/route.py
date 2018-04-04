from . import app
from flask import request, render_template, redirect, url_for
import uuid
import threading
from agent import SmartAgent, RandomAgent, MaxAgent, OptionalAgent, MCTSAgent
from utils import end, generate_available_action, generate_from_action
import queue
import os

k = 10

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


human_queue = {}
agent_queue = {}
mod_list = {}
set_list = {}
step = {}


def gamer(gameid, fb, method, mod):
    f = open(os.path.join(app.config["RESULT_DIR"], gameid + ".txt"), "w")

    if fb == 0:
        print("human vs %s" % method, file=f)
    else:
        print("%s vs human" % method, file=f)

    agent = generate_agent(method)(k, mod)
    step_limit = 75

    while True:
        state = agent_queue[gameid].get()
        if state[0] == -4:
            print("human grant lose, game ends", file=f)
            break
        if state[0] == -2:
            print("human loses, game ends", file=f)
            break
        set_list[gameid].add(state)

        l1, r1, l2, r2, turn = state
        print("%d,%d,%d,%d" % (l1, r1, l2, r2), file=f)
        action_list = generate_available_action(k, l1, r1, l2, r2, turn, set_list[gameid], mod)

        if len(action_list) == 0 or end(l1, r1, l2, r2):
            human_queue[gameid].put((-1, -1, -1, -1, -1))
            print("machine loses,game ends", file=f)
            break

        if turn == 0:
            action = agent.next_step(l1, r1, l2, r2, action_list)
            l1, r1, l2, r2, turn = generate_from_action(k, l1, r1, l2, r2, turn, action_list[action][0],
                                                        action_list[action][1])
        else:
            action = agent.next_step(l2, r2, l1, r1, action_list)
            l1, r1, l2, r2, turn = generate_from_action(k, l1, r1, l2, r2, turn, action_list[action][0],
                                                        action_list[action][1])

        print("%d,%d,%d,%d" % (l1, r1, l2, r2), file=f)
        step[gameid] += 1
        if end(l1, r1, l2, r2):
            human_queue[gameid].put((-2, -2, -2, -2, -2))
            print("human loses,game ends", file=f)
            break

        if step[gameid] >= step_limit:
            human_queue[gameid].put((-3, -3, -3, -3, -3))
            print("draw, game ends", file=f)
            break

        set_list[gameid].add((l1, r1, l2, r2, turn))
        human_queue[gameid].put((l1, r1, l2, r2, turn))

    f.close()
    print("Game %s ends" % gameid)


def gen(gameid, action_list, state, opt):
    able = [[False, False], [False, False]]
    check = [[False, False], [False, False]]
    if opt < 0:
        if opt == -1:
            info = "你赢了"
        elif opt == -2:
            info = "你输了"
        elif opt == -3:
            info = "平局了"
        elif opt == -4:
            info = "你认输了"
        else:
            info = "出现了错误"

        human_queue[gameid].put((opt, opt, opt, opt, opt))

        return render_template("game.html", gameid=gameid, able=able, inf=info, action_able=False,
                               state=state, check=check)

    for op1, op2 in action_list:
        able[op1][op2] = True

    if able[0][0]:
        check[0][0] = True
    elif able[0][1]:
        check[0][1] = True
    elif able[1][0]:
        check[1][0] = True
    elif able[1][1]:
        check[1][1] = True

    return render_template("game.html", gameid=gameid, able=able, inf="", action_able=True, state=state,
                           check=check)


@app.route("/getaction")
def action():
    op1 = int(request.args["op"]) // 2
    op2 = int(request.args["op"]) % 2
    gameid = request.args["gameid"]

    state = request.args["state"].replace("(", "").replace(")", "").replace(" ", "").split(",")
    l1 = int(state[0])
    r1 = int(state[1])
    l2 = int(state[2])
    r2 = int(state[3])
    turn = int(state[4])
    # print("haha1", l1, r1, l2, r2, turn)
    l1, r1, l2, r2, turn = generate_from_action(k, l1, r1, l2, r2, turn, op1, op2)
    # print("haha2", l1, r1, l2, r2, turn)
    step[gameid] += 1

    agent_queue[gameid].put((l1, r1, l2, r2, turn))
    return redirect(url_for("human_agent", gameid=gameid))


@app.route("/game")
def human_agent():
    if not ("gameid" in request.args):
        return "gg"
    else:
        gameid = request.args["gameid"]

        state = human_queue[gameid].get()
        # print("get", state)
        l1, r1, l2, r2, turn = state
        if l1 < 0:
            return gen(gameid, [], state, l1)

        action_list = generate_available_action(k, l1, r1, l2, r2, turn, set_list[gameid], mod_list[gameid])
        if len(action_list) == 0:
            agent_queue[gameid].put((-2, -2, -2, -2, -2))

            return gen(gameid, [], state, -2)

        return gen(gameid, action_list, state, 0)


def start_game(fb, method, mod):
    uid = str(uuid.uuid4())
    human_queue[uid] = queue.Queue()
    agent_queue[uid] = queue.Queue()
    mod_list[uid] = mod
    set_list[uid] = set()
    set_list[uid].add((1, 1, 1, 1, 0))
    step[uid] = 0

    if fb == 0:
        human_queue[uid].put((1, 1, 1, 1, 0))
    else:
        agent_queue[uid].put((1, 1, 1, 1, 0))

    threading.stack_size(200000000)
    thread = threading.Thread(target=gamer, args=(uid, fb, method, mod))
    thread.start()

    return uid


@app.route("/")
def main():
    if not ("fb" in request.args) or not ("method" in request.args) or not ("mod" in request.args):
        return render_template("main.html")
    else:
        fb = int(request.args["fb"])
        method = request.args["method"]
        mod = int(request.args["mod"])
        uid = start_game(fb, method, mod)

        return redirect(url_for("human_agent", gameid=uid))
