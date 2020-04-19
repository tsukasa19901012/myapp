import numpy as np
import random
import sys

class CommonFunc:
    def __init__(self, mystone, opponentstone):
        self.mystone = mystone
        self.opponentstone = opponentstone

    def getStoneLocation(self):
        # 相手stoneの座標のリストを返す
        locaList = list(zip(*np.where(field == self.opponentstone)))
        return locaList

    def getNextLocation(self):
        # 相手stoneの隣マス(8方向)の座標のリストを返す
        sl = self.getStoneLocation()
        locaList = []
        for x, y in sl:
            for i, j in offset:
                t = (x+i, y+j)
                locaList.append(t)
        return locaList

    def getEmptyLocation(self):
        # 空のマスを返す
        locaList = list(zip(*np.where(field == 0)))
        return locaList

    def getPossibleLocation(self):
        # 石を置くことが出来るマスを返す
        nl = self.getNextLocation()
        el = self.getEmptyLocation()
        andList = list(set(nl) & set(el))
        locaDict = {}
        for x, y in andList:
            offsetList = []
            for i, j in offset:
                xpos, ypos = x + i, y + j
                while((0 <= xpos and xpos < field.shape[0]) and (0 <= ypos and ypos < field.shape[1])):
                    if(field[xpos, ypos] == self.opponentstone):
                        xpos = xpos + i
                        ypos = ypos + j
                        continue
                    elif(field[xpos, ypos] == self.mystone):
                        if(2 <= abs(xpos - x) or 2 <= abs(ypos - y)):
                            offsetList.append((i, j))
                        break
                    else:
                        break
            if(len(offsetList) != 0):
                locaDict[(x, y)] = offsetList
        return locaDict

    def updateField(self, pos):
        # fieldの更新を行う
        possibleDict = self.getPossibleLocation()
        field[pos[0], pos[1]] = self.mystone
        for x, y in possibleDict[pos]:
            xpos = pos[0] + x
            ypos = pos[1] + y
            while((0 <= xpos and xpos < field.shape[0]) and (0 <= ypos and ypos < field.shape[1])):
                if(field[xpos, ypos] == self.opponentstone):
                    field[xpos, ypos] = self.mystone
                    xpos = xpos + x
                    ypos = ypos + y
                else:
                    break

class Player(CommonFunc):
    def address2pos(self, address):
        if(address in addressTable):
            tlist = list(zip(*np.where(addressTable == address)))
            pos = tlist[0]
            return pos
    def confPos(self, pos):
        if(pos in self.getPossibleLocation()):
            return True
        return False

class Computer(CommonFunc):
    def electRandom(self):
        pl = self.getPossibleLocation()
        if(len(pl) == 0):
            print("pass")
            return
        r = random.randrange(0, len(pl))
        for i in enumerate(pl):
            if(i[0] == r):
                return i[1]
        print("Error : electRandom")
        sys.exit()


def printHeader():
    alpha = ["a", "b", "c", "d", "e", "f", "g", "h"]
    print("")
    print("   ", end="")
    for i in alpha:
        print("   {0} ".format(i), end="")
    pass

def printField():
    printHeader()
    print("")
    print("   +" + "----+"*8)
    for i in range(field.shape[0]):
        row = i + 1
        print(" {0} |".format(row), end="")
        for j in range(field.shape[1]):
            if(field[i, j] == 0):
                print("    ", end="")
            elif(field[i, j] == 1):
                print(" ○ ", end="")
            elif(field[i, j] == 2):
                print(" ● ", end="")
            #print(" " + str(field[i, j]), "|", end="")
            print("|", end="")
        print("")
        print("   +" + "----+"*8)
    #print("+" + "--+"*8)
    pass

def printCmd():
    print(" 黒駒：○")
    print(" 白駒：●")
    print(" マスの指定の仕方（例）: a1, g8")
    print(" アルファベット、数字の順で指定")

def setStone():
    print("先攻と後攻どちらにしますか？")
    print("先攻：1")
    print("後攻：2")
    turn = input("数字を入力してください：")
    if(turn == "1"):
        playerStone = 1
        computerStone = 2
        Turn = playerStone
    elif(turn == "2"):
        playerStone = 2
        computerStone = 1
        Turn = computerStone
    else:
        print("終了します。")
        sys.exit()
    return playerStone, computerStone, Turn

def confResult():
    ps = len(list(zip(*np.where(field == playerStone))))
    cs = len(list(zip(*np.where(field == computerStone))))
    if(ps > cs):
        return 'Winner : You'
    elif(ps < cs):
        return 'Winner : Computer'
    else:
        return 'Result : Draw'

def setField():
    field = np.array([[0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,2,1,0,0,0],
                      [0,0,0,1,2,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0]])
    return field

# global 変数
global playerStone
global computerStone
global Turn

global field
field = setField()
global offset
offset = [(-1, -1), (-1, 0), (-1, 1),
          ( 0, -1),          ( 0, 1),
          ( 1, -1), ( 1, 0), ( 1, 1)]

global addressTable
addressTable = np.array([["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
                         ["a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2"],
                         ["a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3"],
                         ["a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4"],
                         ["a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5"],
                         ["a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6"],
                         ["a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7"],
                         ["a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"]])



def main():
    # main loop
    playcount = 0
    while(playcount == 0):
        # 盤面を初期状態にする
        global field
        field = setField()
        # 先攻後攻を決める
        global playerStone
        global computerStone
        global Turn
        playerStone, computerStone, Turn = setStone()

        global player
        global comp
        player = Player(playerStone, computerStone)
        comp = Computer(computerStone, playerStone)

        # 盤面の表示
        printField()
        printCmd()

        # play loop
        while(True):
            if(Turn == playerStone):
                pl = player.getPossibleLocation()
                if(len(pl) == 0):
                    # pass
                    print("pass")
                    Turn = computerStone
                else:
                    address = input("棋譜を選択してください：")
                    if(address in ["End", "end"]):
                        sys.exit()
                    pos = player.address2pos(address)
                    if(player.confPos(pos)):
                        player.updateField(pos)
                        Turn = computerStone
                    else:
                        print("{0}を選択することはできません。".format(address))
                        print("")
                        continue
            elif(Turn == computerStone):
                pos = comp.electRandom()
                if(pos == None):
                    # pass
                    Turn = playerStone
                else:
                    comp.updateField(pos)
                    Turn = playerStone
            else:
                print("終了します。")
                break

            # 盤面表示
            printField()

            # 勝利判定
            if(len(player.getPossibleLocation()) == 0 and len(comp.getPossibleLocation()) == 0):
                print("オセロを終了します。")
                print("まで、{0}手".format(playcount))
                print(confResult())
                break
            playcount += 1

        # Question : continue
        print("Continue? (New Game)")
        ans = input("Yes(y) / No(n) : ")
        if(ans in ["No", "no", "n"]):
            break
        playcount = 0
        print("================== New Game ====================")
    pass

if __name__ == '__main__':
    main()
