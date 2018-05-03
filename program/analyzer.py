import os

res = [{}, {}]

for file_name in os.listdir("result"):
    f = open(os.path.join(file_name), "r")

    line = f.readline()[:-1].split(" vs ")
    op1 = line[0]
    op2 = line[1]

    mod = int(f.readline()[-2])
    if not (op1 in res[mod].keys()):
        res[mod][op1] = {}
    if not (op2 in res[mod][op1].keys()):
        res[mod][op1][op2] = [0, 0, 0, 0, 0]

    last_line = ""
    cnt = 0
    for line in f:
        last_line = line
        cnt += 1
    cnt -= 1

    if last_line.startswith("human loses"):
        if op1 == "human":
            res[mod][op1][op2][2] += 1
            res[mod][op1][op2][3] += cnt
        else:
            res[mod][op1][op2][0] += 1
            res[mod][op1][op2][1] += cnt
    elif last_line.startswith("machine loses"):
        if op1 == "human":
            res[mod][op1][op2][0] += 1
            res[mod][op1][op2][1] += cnt
        else:
            res[mod][op1][op2][2] += 1
            res[mod][op1][op2][3] += cnt
    elif last_line.startswith("draw"):
        res[mod][op1][op2][4] += 1

for x in res:
    for y in x.keys():
        for z in y.keys():
            print(x, y, z, res[x][y][z])
