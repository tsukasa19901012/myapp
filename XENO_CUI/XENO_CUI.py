import random, copy

# カードのクラス作成
class Card:
    def __init__(self, rank, name, efficacy, efficacyContent, image):
        self.rank = rank # カードランク
        self.name = name # カード名
        self.efficacy = efficacy # カード効果
        self.efficacyContent = efficacyContent # カード効果内容
        self.image = image # カード画像

# カードの辞書
cardDict = {
      1: Card("1", "少年", "革命", "1枚目の捨て札は何の効果も発動しないが、場に2枚目が出た時には皇帝と同じ効果「公開処刑」が発動する", "xeno01.jpg")
    , 2: Card("2", "兵士", "捜査", "指名した相手の手札を言い当てると相手は脱落する。", "xeno02.jpg")
    , 3: Card("3", "占師", "透視", "指名した相手の手札を見る。", "xeno03.jpg")
    , 4: Card("4", "乙女", "守護", "次の自分の手番まで自分への効果を無効にする。", "xeno04.jpg")
    , 5: Card("5", "死神", "疫病", "指名した相手に山札から1枚引かせる。2枚になった相手の手札を非公開にさせたまま、1枚を指定して捨てさせる。", "xeno05.jpg")
    , 6: Card("6", "貴族", "対決", "指名した相手と手札を見せ合い、数字の小さい方が脱落する。見せ合う際は他のプレイヤーに見られないよう密かに見せ合う。", "xeno06.jpg")
    , 7: Card("7", "賢者", "選択", "次の手番で山札から１枚引くかわりに３枚引き、そのうち１枚を選ぶことができる。残り２枚は山札へ戻す。", "xeno07.jpg")
    , 8: Card("8", "精霊", "交換", "指名した相手の手札と自分の持っている手札を交換する。", "xeno08.jpg")
    , 9: Card("9", "皇帝", "公開処刑", "指名した相手に山札から1枚引かせて、手札を2枚とも公開させる。そしてどちらか1枚を指定し捨てさせる。", "xeno09.jpg")
    , 10: Card("10", "英雄", "潜伏・転生", "場に出すことができず、捨てさせられたら脱落する。皇帝以外に脱落させられた時に転生札で復活する。", "xeno10.jpg")
}

# 賢者フラグ
playerKenjaFlg = False
cpuKenjaFlg = False

# 乙女フラグ
playerOtomeFlg = False
cpuOtomeFlg = False

# 手札
player_Hand = []
cpu_Hand = []

# 捨札
player_Discard = []
cpu_Discard = []

print('XENOを始めます。')

'''
ドロー
kenjaFlg: 賢者フラグ
playerFlg: プレイヤー手番フラグ
'''
def drawCard(kenjaFlg, playerFlg):
    global player_Hand
    global cpu_Hand
    global deck
    # 賢者が使われているか確認
    if kenjaFlg:
        # プレイヤー手番チェック
        if playerFlg:
            deckCnt = len(deck)
            # 3枚までドロー(デッキが3枚より少ない場合はデッキ枚数)
            drawList = []
            for i in range(deckCnt):
                if i > 2 :
                    break
                drawList.append(deck.pop(0))

            # 引いたカードを表示
            print('賢者の効果で引いた3枚のカードを表示します。')
            for index, card in  enumerate(drawList):
                print('[' + card.rank + '] ' + card.name)
            print('\n')

            # プレイヤーの手札を表示
            print('プレイヤーの手札')
            for index, card in  enumerate(player_Hand):
                print('[' + card.rank + '] ' + card.name)
            print('\n')

            # プレイヤーの捨て札を表示
            print('プレイヤーの捨て札')
            for index, card in  enumerate(player_Discard):
                print('[' + card.rank + '] ' + card.name)
            print('\n')

            # cpuの捨て札を表示
            print('cpuの捨て札')
            for index, card in  enumerate(cpu_Discard):
                print('[' + card.rank + '] ' + card.name)
            print('\n')

            print('ドローするカードを選んでください\n')
            while True:
                try:
                    playerUseNum = input('数字を入力：')
                    print('')
                    if drawNum_check(drawList, playerUseNum):
                        for index, card in  enumerate(drawList):
                            if playerUseNum == card.rank:
                                # 手札に入れる
                                player_Hand.append(drawList.pop(drawList.index(card)))
                            else:
                                # 山札に戻す
                                deck.append(drawList.pop(drawList.index(card)))
                        # デッキをシャッフル
                        random.shuffle(deck)
                        break
                except:
                    pass
                print('カードがありません。再入力してください\n')
        else:
           # 3枚のうちランダムに1枚をドロー
           cpu_Hand.append(deck.pop(random.randint(0,2)))
    else:
       # プレイヤー手番チェック
        if playerFlg:
            # 1枚ドロー
            player_Hand.append(deck.pop(0))
        else:
            # 1枚ドロー
            cpu_Hand.append(deck.pop(0))

'''
ドロー番号入力チェック
'''
def drawNum_check(drawList, num):
    # 数値チェック
    if not str.isdecimal(num):
        print('数値以外が入力されています。')
        return False
    # 1-10の数値チェック
    numInt = int(num)
    if numInt < 1 or 10 < numInt:
        print('1-10以外が入力されています。')
        return False
    # 手札存在チェック
    for index, card in  enumerate(drawList):
        if num == card.rank:
            return True
    print('対象以外のものが入力されています。')
    return False   


'''
使うカードとして入力したカードが正しいかチェック
num: 入力した数値
'''
def useNum_check(num):
    # 数値チェック
    if not str.isdecimal(num):
        print('数値以外が入力されています。')
        return False
    # 1-10の数値チェック
    numInt = int(num)
    if numInt < 1 or 10 < numInt:
        print('1-10以外が入力されています。')
        return False
    # 10は出せない
    if numInt == 10:
        print('[10] 英雄 は出せません。')
        return False
    # 手札存在チェック
    for index, card in  enumerate(player_Hand):
        if num == card.rank:
            return True
    print('手札にないものが入力されています。')
    return False

'''
2の効果入力チェック
num: 入力した数値
'''
def useNum_two_efficacy_check(num):
    # 数値チェック
    if not str.isdecimal(num):
        print('数値以外が入力されています。')
        return False
    # 1-10の数値チェック
    numInt = int(num)
    if numInt < 1 or 10 < numInt:
        print('1-10以外が入力されています。')
        return False
    return True


'''
カード効果
playerFlg: プレイヤー手番フラグ
useNum: 使うカード
'''
def efficacyAction(playerFlg, useNum):
    global player_Hand
    global cpu_Hand
    global playerKenjaFlg
    global cpuKenjaFlg
    global playerOtomeFlg
    global cpuOtomeFlg
    global deck

    # プレイヤー
    if playerFlg:
        for index, card in  enumerate(player_Hand):
            if useNum == card.rank:
                # 捨て札に移動
                player_Discard.append(player_Hand.pop(player_Hand.index(card)))

        # 効果
        playerKenjaFlg = False
        if '1' == useNum:
            #捨て札に1があるかチェック
            oneCnt = player_Discard.count(cardDict[1]) + cpu_Discard.count(cardDict[1])
            if 2 == oneCnt:
                if cpuOtomeFlg:
                    print('乙女の効果で無効にされました。')
                    cpuOtomeFlg = False
                    return 0
                # 捨て札に1がある場合
                print('TODO 9の効果')
        elif '2' == useNum:
            if cpuOtomeFlg:
                print('乙女の効果で無効にされました。')
                cpuOtomeFlg = False
                return 0
            # cpuの手札を予想する。
            print('予測する相手の手札を入力してください\n')
            while True:
                try:
                    twoEfficacy = input('数字を入力：')
                    print('')
                    if useNum_two_efficacy_check(playerUseNum):
                        break
                except:
                    pass
                print('再入力してください\n')
            # cpuの手札を当てれば勝ち
            if cardDict[int(twoEfficacy)] in cpu_Hand:
                return 1
            else:
                print('予想は外れました。')
        elif '3' == useNum:
            if cpuOtomeFlg:
                print('乙女の効果で無効にされました。')
                cpuOtomeFlg = False
                return 0
            # cpuの手札を表示
            threeEfficacy = cpu_Hand[0]
            print( 'cpuの手札は' + '[' + threeEfficacy.rank + '] ' + threeEfficacy.name + 'です。' )
        elif '4' == useNum:
            playerOtomeFlg = True
            return 0
        elif '5' == useNum:
            if cpuOtomeFlg:
                print('乙女の効果で無効にされました。')
                cpuOtomeFlg = False
                return 0
            # cpuがドローして、ランダムに1枚捨てる。
            cpu_Hand.append(deck.pop(0))
            cpu_Discard.append(cpu_Hand.pop(random.randint(0,1)))
        elif '6' == useNum:
            print('手札の数字が大きい方が勝ちです。')
            sixPlayerCard = player_Hand.pop(0)
            sixCpuCard = cpu_Hand.pop(0)
            if int(sixPlayerCard.rank) == int(sixCpuCard.rank):
                return 3
            elif int(sixPlayerCard.rank) > int(sixCpuCard.rank):
                return 1
            else:
                return 2
        elif '7' == useNum:
            playerKenjaFlg = True

    # cpu
    else:
        for index, card in  enumerate(cpu_Hand):
            if useNum == card.rank:
                # 捨て札に移動
                cpu_Discard.append(cpu_Hand.pop(cpu_Hand.index(card)))

        # 効果
        cpuKenjaFlg = False
        if '4' == useNum:
            cpuOtomeFlg = True
            return 0
        if '7' == useNum:
            cpuKenjaFlg = True

    playerOtomeFlg = False
    cpuOtomeFlg = False
    return 0

# カードをリストで作成
masterCard = []
masterCard.append(cardDict[1])
masterCard.append(cardDict[1])
masterCard.append(cardDict[2])
masterCard.append(cardDict[2])
masterCard.append(cardDict[3])
masterCard.append(cardDict[3])
masterCard.append(cardDict[4])
masterCard.append(cardDict[4])
masterCard.append(cardDict[5])
masterCard.append(cardDict[5])
masterCard.append(cardDict[6])
masterCard.append(cardDict[6])
masterCard.append(cardDict[7])
masterCard.append(cardDict[7])
masterCard.append(cardDict[8])
masterCard.append(cardDict[8])
masterCard.append(cardDict[9])
masterCard.append(cardDict[10])

# デッキを作成
deck = copy.copy(masterCard)

# デッキをシャッフル
random.shuffle(deck)

# デッキの一番下のカードを転生札に設定する
reincarnationCard = deck.pop(-1)

# 手札を配る
player_Hand.append(deck.pop(0))
cpu_Hand.append(deck.pop(0))

print('---------------------------------------------------')
print('ゲームを開始します\n')

while True:
    print('---------------------------------------------------')
    # プレイヤーのターン
    while True:
        print('プレイヤーのターンです。')
        # ドロー
        drawCard(playerKenjaFlg, True)

        # プレイヤーの手札を表示
        print('プレイヤーの手札')
        for index, card in  enumerate(player_Hand):
            print('[' + card.rank + '] ' + card.name)
        print('\n')

        # プレイヤーの捨て札を表示
        print('プレイヤーの捨て札')
        for index, card in  enumerate(player_Discard):
            print('[' + card.rank + '] ' + card.name)
        print('\n')

        # cpuの捨て札を表示
        print('cpuの捨て札')
        for index, card in  enumerate(cpu_Discard):
            print('[' + card.rank + '] ' + card.name)
        print('\n')

        print('使うカードを選んでください\n')
        while True:
            try:
                playerUseNum = input('数字を入力：')
                print('')
                if useNum_check(playerUseNum):
                    break
            except:
                pass
            print('再入力してください\n')

        # プレイヤーのターン終了
        break

    # カードの効果
    winFlg = efficacyAction(True, playerUseNum)
    if 1 == winFlg:
        print('プレイヤーの勝ちです\n')
        break
    if 2 == winFlg:
        print('cpuの勝ちです\n')
        break
    if 3 == winFlg:
        print('引き分けです\n')
        break

    # デッキの枚数確認
    if len(deck) == 0:
        print('山札がありません。')
        lastFlg = 1
        break

    print('-----------------------------------------------------')
    # cpuのターン
    while True:
        print('cpuのターンです。')
        # ドロー
        drawCard(cpuKenjaFlg, False)

        # cpuが使うカード
        cpuUseNum = cpu_Hand[random.randint(0,1)].rank
        print('cpuが使ったカードは' + cpuUseNum + 'です')

        # cpuのターン終了
        break
    # カードの効果
    winFlg = efficacyAction(False, cpuUseNum)
    if 1 == winFlg:
        print('プレイヤーの勝ちです\n')
        break
    if 2 == winFlg:
        print('cpuの勝ちです\n')
        break
    if 3 == winFlg:
        print('引き分けです\n')
        break

    # デッキの枚数確認
    if len(deck) == 0:
        print('山札がありません。')
        lastFlg = 1
        break

# lastFlgが1の場合は手札勝負
if lastFlg == 1:
    lastPlayerCard = player_Hand.pop(0)
    lastCpuCard = cpu_Hand.pop(0)

    if int(lastPlayerCard.rank) == int(lastCpuCard.rank):
        print('引き分けです\n')
    elif int(lastPlayerCard.rank) > int(lastCpuCard.rank):
        print('プレイヤーの勝ちです\n')
    else:
        print('cpuの勝ちです\n')
print('ゲームを終了します')

