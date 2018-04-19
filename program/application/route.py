from . import app
import os
import time
from flask import request, render_template, redirect, url_for, send_from_directory
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


game_list = {}


def init_game(game_id, mod, turn):
    game_list[game_id] = {
        "set": set(),
        "mod": mod,
        "history": [(1, 1, 1, 1, 0)],
        "turn": turn
    }


def gamer(game_id, fb, method, mod):
    f = open(os.path.join(app.config["RESULT_DIR"], game_id + ".txt"), "w")

    if fb == 0:
        print("human vs %s" % method, file=f)
    else:
        print("%s vs human" % method, file=f)
    print("Mod %d" % mod, file=f)

    agent = generate_agent(method)(k, mod)
    step_limit = 75

    wait_second = 0
    max_wait_second = 100
    while True:
        l = len(game_list[game_id]["history"])
        if l % 2 != game_list[game_id]["turn"]:
            wait_second += 1
            if wait_second > max_wait_second:
                game_list[game_id]["history"].append((-6, -6, -6, -6, -6))
                print("human leaves, game ends", file=f)
                break
            time.sleep(1)
            continue

        state = game_list[game_id]["history"][-1]
        wait_second = 0

        if state[0] == -4:
            print("human grant lose, game ends", file=f)
            break
        if state[0] == -2:
            print("human loses, game ends", file=f)
            break

        game_list[game_id]["set"].add(state)

        l1, r1, l2, r2, turn = state
        print("%d,%d,%d,%d" % (l1, r1, l2, r2), file=f)

        action_list = generate_available_action(k, l1, r1, l2, r2, turn, game_list[game_id]["set"], mod)

        if len(action_list) == 0 or end(l1, r1, l2, r2):
            game_list[game_id]["history"].append((-1, -1, -1, -1, -1))
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

        game_list[game_id]["set"].add((l1, r1, l2, r2, turn))
        game_list[game_id]["history"].append((l1, r1, l2, r2, turn))

        if end(l1, r1, l2, r2):
            game_list[game_id]["history"].append((-2, -2, -2, -2, -2))
            print("human loses,game ends", file=f)
            break

        if len(game_list[game_id]["history"]) >= step_limit:
            game_list[game_id]["history"].append((-3, -3, -3, -3, -3))
            print("draw, game ends", file=f)
            break

    f.close()
    print("Game %s ends" % game_id)


@app.route("/getaction")
def action():
    op1 = int(request.args["op"]) // 2
    op2 = int(request.args["op"]) % 2
    game_id = request.args["gameid"]
    if game_list[game_id]["history"][-1][0] < 0:
        return redirect(url_for("human_agent", gameid=game_id, step=len(game_list[game_id]["history"])))

    state = request.args["state"].replace("(", "").replace(")", "").replace(" ", "").split(",")
    l1 = int(state[0])
    r1 = int(state[1])
    l2 = int(state[2])
    r2 = int(state[3])
    turn = int(state[4])
    # print("haha1", l1, r1, l2, r2, turn)
    l1, r1, l2, r2, turn = generate_from_action(k, l1, r1, l2, r2, turn, op1, op2)
    # print("haha2", l1, r1, l2, r2, turn)
    step = len(game_list[game_id]["history"]) + 2

    game_list[game_id]["history"].append((l1, r1, l2, r2, turn))
    return redirect(url_for("human_agent", gameid=game_id, step=step))


def gen(game_id, action_list, state):
    able = [[False, False], [False, False]]
    check = [[False, False], [False, False]]
    opt = state[0]
    if opt < 0:
        if len(game_list[game_id]["history"]) % 2 != game_list[game_id]["turn"]:
            game_list[game_id]["history"].append(state)

        cnt = len(game_list[game_id]["history"]) - 1
        while game_list[game_id]["history"][cnt][0] < 0:
            cnt -= 1
        state = game_list[game_id]["history"][cnt]
        if state[4] == game_list[game_id]["turn"]:
            cnt -= 1
            state = game_list[game_id]["history"][cnt]
        cnt -= 1
        if cnt >= 0:
            state2 = game_list[game_id]["history"][cnt]
        else:
            state2 = ""
        cnt -= 1
        if cnt >= 0:
            state3 = game_list[game_id]["history"][cnt]
        else:
            state3 = ""

        if opt == -1:
            info = "机器无路可走，你已冠绝群雄，取得胜利"
        elif opt == -2:
            info = "机器不可战胜，你已经输了"
        elif opt == -3:
            info = "棋逢对手，平局了"
        elif opt == -4:
            info = "你认为已经平局了，虽然我们也不知道是不是真的平局了"
        elif opt == -6:
            info = "你离开游戏太久了，机器睡觉去了，所以游戏结束了"
        elif opt == -7:
            info = "你输了，因为再移动会到重复状态了"
        else:
            info = "出现了错误，请关机睡觉"

        return render_template("game.html", gameid=game_id, able=able, inf=info, action_able=False,
                               state=state, check=check, mod=game_list[game_id]["mod"], state2=state2, state3=state3)

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

    cnt = len(game_list[game_id]["history"]) - 2
    if cnt >= 0:
        state2 = game_list[game_id]["history"][cnt]
    else:
        state2 = ""
    cnt -= 1
    if cnt >= 0:
        state3 = game_list[game_id]["history"][cnt]
    else:
        state3 = ""

    return render_template("game.html", gameid=game_id, able=able, inf="", action_able=True, state=state,
                           check=check, mod=game_list[game_id]["mod"], state2=state2, state3=state3)


@app.route("/game")
def human_agent():
    if not ("gameid" in request.args) or not (request.args["gameid"] in game_list.keys()):
        return redirect(url_for("main"))
    else:
        game_id = request.args["gameid"]
        if not ("step" in request.args):
            step = 1 + game_list[game_id]["turn"]
        else:
            step = int(request.args["step"])

        while True:
            if "pingju" in request.args:
                state = (-4, -4, -4, -4, -4)
                break

            state = game_list[game_id]["history"][-1]

            if state[0] < 0:
                break

            if step != len(game_list[game_id]["history"]):
                continue

            if len(game_list[game_id]["history"]) % 2 == game_list[game_id]["turn"]:
                continue

            break

        if state[0] < 0:
            return gen(game_id, [], state)

        l1, r1, l2, r2, turn = state

        action_list = generate_available_action(k, l1, r1, l2, r2, turn, game_list[game_id]["set"],
                                                game_list[game_id]["mod"])

        if len(action_list) == 0:
            state = (-7, -7, -7, -7, -7)

            return gen(game_id, [], state)

        return gen(game_id, action_list, state)


def start_game(fb, method, mod):
    uid = str(uuid.uuid4())
    init_game(uid, mod, fb)

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


@app.route('/static/<path:filetype>/<path:filename>')
def serve_static(filetype, filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join('static', filetype),
                               filename)
