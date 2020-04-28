# -*- coding: utf-8 -*-
import sys, random
sys.dont_write_bytecode = True

from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
LabelBase.register(DEFAULT_FONT, "ipaexg.ttf")
from kivy.app import App
from kivy.core.window import Window
Window.size = (480, 720)

from kivy.factory import Factory

# 処理一時停止のための機能
def start_generator(gen):
    def step_gen(*args, **kwargs):
        try:
            gen.send((args, kwargs, ))(step_gen)
        except StopIteration:
            pass
    try:
        gen.send(None)(step_gen)
    except StopIteration:
        pass
def event(ed, name):
    bind_id = None
    step_gen = None
    def bind(step_gen_):
        nonlocal bind_id, step_gen
        bind_id = ed.fbind(name, callback)
        assert bind_id > 0  # bindingに成功したか確認
        step_gen = step_gen_
    def callback(*args, **kwargs):
        ed.unbind_uid(name, bind_id)
        step_gen(*args, **kwargs)
    return bind

# カード情報クラス
class Card:
    def __init__(self, rank, name, efficacy, efficacyContent, image):
        self.rank = rank # カードランク
        self.name = name # カード名
        self.efficacy = efficacy # カード効果
        self.efficacyContent = efficacyContent # カード効果内容
        self.image = image # カード画像

# カード詳細画面
class CardInFoModal(Factory.ModalView):
    def __init__(self, card):
        super().__init__()
        # カードタイトル
        self.ids.cardTittle.text = '【' + card.rank + '】' + card.name
        # カード画像
        self.ids.cardImage.source = card.image
        # カード効果
        self.ids.cardEfficacy.text = '【' + card.efficacy + '】' + card.efficacyContent

# カード画像クラス
class CardImage(Factory.Image):
    # 表カード押下時
    def on_touch_down(self, touch):
        # クリック位置
        spos = touch.spos
        opos = touch.opos
        # カードが裏向きのもの（cpuの手札の場合）
        if self.num == 0 :
            return
        # 対象のカード上でクリックした場合
        if self.x <= opos[0] <= self.right and self.y <= opos[1] <= self.top :
            modal = Factory.CardBubbleModal(pos_hint={'x': spos[0], 'center_y': spos[1] })
            # カードが10、手札以外のカードの場合
            if self.playCardButtonDispFlg == 0:
                # 吹き出しのカードを出すボタンを除外
                modal.ids.cardBubble.remove_widget(modal.ids.playCardButton)
            else:
                # 吹き出しのカードを出すボタンのイベントを追加
                modal.ids.playCardButton.bind(on_press=self.on_playCardButton)
                pass
            # 吹き出しのカード詳細ボタンのイベントを追加
            modal.ids.caedInfoButton.bind(on_press=self.on_showCardInFoModal)
            # 吹き出しを表示
            modal.open()
            pass
        pass

    # 吹き出しのカード詳細ボタン押下処理
    def on_showCardInFoModal(self, obj):
        cardInFoModal = Factory.CardInFoModal(card = self.card)
        # 吹き出しを削除
        obj.parent.parent.parent.dismiss()
        # カード詳細を表示
        cardInFoModal.open()
        pass

    # 吹き出しのカードを出すボタン押下処理
    def on_playCardButton(self, obj):
        start_generator(self.playCardButtonLogic(obj))

    def playCardButtonLogic(self, obj):
        xenoMainWidget = App.get_running_app().root.children[0]
        # クリックしたカード
        cardNum = self.num
        # カードが手札に含まれているか確認
        if not cardNum in xenoMainWidget.playerHandList:
            return
        # 手札から捨て札にカードを出す
        xenoMainWidget.playerHandList.pop(xenoMainWidget.playerHandList.index(cardNum))
        xenoMainWidget.playerDiscardList.append(cardNum)
        # 吹き出しを削除
        obj.parent.parent.parent.dismiss()
        # 画面更新
        xenoMainWidget.refresh()
        # カード効果発動
        endFlg = xenoMainWidget.activationCardEffect(cardNum)
        yield event(xenoMainWidget.modal, 'on_dismiss')  # modalが閉じられるまで待つ
        # ゲーム終了か確認
        if endFlg == 1:
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # デッキがない場合
        if len(xenoMainWidget.deck) == 0:
            # 対決を行う
            xenoMainWidget.sixfficacy()
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # cpu処理
        xenoMainWidget.cpuTurnLogic()     
        pass

# メイン画面
class XenoMainWidget(Factory.FloatLayout):
    # カードの辞書
    cardDict = {
          1: Card("1", "少年", "革命", "1枚目の捨て札は何の効果も発動しないが、場に2枚目が出た時には皇帝と同じ効果「公開処刑」が発動する", "card1.png")
        , 2: Card("2", "兵士", "捜査", "指名した相手の手札を言い当てると相手は脱落する。", "card2.png")
        , 3: Card("3", "占師", "透視", "指名した相手の手札を見る。", "card3.png")
        , 4: Card("4", "乙女", "守護", "次の自分の手番まで自分への効果を無効にする。", "card4.png")
        , 5: Card("5", "死神", "疫病", "指名した相手に山札から1枚引かせる。2枚になった相手の手札を非公開にさせたまま、1枚を指定して捨てさせる。", "card5.png")
        , 6: Card("6", "貴族", "対決", "1on1の場合1枚目の捨て札は相手と手札を見せ合う。2枚目か3人以上の場合は指名した相手と手札を見せ合い、数字の小さい方が脱落する。見せ合う際は他のプレイヤーに見られないよう密かに見せ合う。", "card6.png")
        , 7: Card("7", "賢者", "選択", "次の手番で山札から１枚引くかわりに３枚引き、そのうち１枚を選ぶことができる。残り２枚は山札へ戻す。", "card7.png")
        , 8: Card("8", "精霊", "交換", "指名した相手の手札と自分の持っている手札を交換する。", "card8.png")
        , 9: Card("9", "皇帝", "公開処刑", "指名した相手に山札から1枚引かせて、手札を2枚とも公開させる。そしてどちらか1枚を指定し捨てさせる。", "card9.png")
        , 10: Card("10", "英雄", "潜伏・転生", "場に出すことができず、捨てさせられたら脱落する。皇帝以外に脱落させられた時に転生札で復活する。", "card10.png")
    }
    def __init__(self, turn, **kwargs):
        super().__init__(**kwargs)
        # ターンを設定
        self.turn = turn
        # デッキを作成する
        self.deck = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,10]
        random.shuffle(self.deck)

        # デッキの一番下のカードを転生札に設定する
        self.reincarnationCard = self.deck.pop(-1)

        # 手札を配る
        self.playerHandList.append(self.deck.pop(0))
        self.cpuHandList.append(self.deck.pop(0))

        if self.turn == 1 :
            self.drawDeck()
        else:
            self.cpuTurnLogic()
        
        # 画面更新
        self.refresh()
        pass

    # デッキから1枚ドローする
    def drawDeck(self):
        # ターンの確認
        if self.turn == 1:
            # プレイヤーのターン
            self.playerHandList.append(self.deck.pop(0))
        else:
            # cpuのターン
            self.cpuHandList.append(self.deck.pop(0))
        # 画面更新
        self.refresh() 
        pass

    # CPUのターン処理
    def cpuTurnLogic(self):
        # デッキがドローできるか確認
        if len(self.deck) == 0:
            return
        # ターンフラグをcpuにする
        self.turn = 2
        # ドローする
        self.drawDeck()
        # 画面更新
        self.refresh()
        # cpuがカードを出す
        self.cpuPlayCard()
        # プレイヤーにドローさせる。
        self.turn = 1
        self.drawDeck()
        # 画面更新
        self.refresh() 
        pass

    # cpuがカードを出す
    def cpuPlayCard(self):
        # ランダムにカードを選択する
        cardNum = 0
        while True:
            cardNum = self.cpuHandList[random.randint(0,1)]
            if cardNum != 10:
                break
        # カードが手札に含まれているか確認
        if not cardNum in self.cpuHandList:
            return
        # 手札から捨て札にカードを出す
        self.cpuHandList.pop(self.cpuHandList.index(cardNum))
        self.cpuDiscardList.append(cardNum)
        # 画面更新
        self.refresh() 
        # カード効果発動
        endFlg = self.activationCardEffect(cardNum)
        # ゲーム終了か確認
        if endFlg == 1:
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # 画面更新
        self.refresh() 
        pass

    # カード効果発動
    def activationCardEffect(self, cardNum):
        # 1のカードを出す処理
        def oneEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            self.modal.open()
            return 0

        # 2のカードの出す処理
        def twoEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            self.modal.open()
            return 0

        # 3のカードを出す処理
        def threeEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.resultLabelText = 'あなたは' + str(cardNum) + 'を出しました。'
                cpuCard = self.cpuHandList[0]
                self.modal.ids.box.add_widget(Factory.Label(text='CPUの手札は' + str(cpuCard) + 'です。'))
            else:
                self.modal.resultLabelText = 'CPUは' + str(cardNum) + 'を出しました。'
                playerCard = self.playerHandList[0]
                self.modal.ids.box.add_widget(Factory.Label(text='プレイヤーの手札は' + str(playerCard) + 'です。'))
            self.modal.open()
            return 0

        # 4のカードを出す処理
        def fourEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            self.modal.open()
            return 0

        # 5のカードを出す処理
        def fiveEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            self.modal.open()
            return 0

        # 6のカードを出す処理
        def sixfficacy(self):
            returnFlg = 0
            # 互いの手札を取得
            playerCard = self.playerHandList[0]
            cpuCard = self.cpuHandList[0]

            # 1枚目か2枚目かを判定
            if 2 == self.playerDiscardList.count(6) + self.cpuDiscardList.count(6) :
                # 2枚目の場合
                # 勝利判定
                resultText = ''
                if playerCard == cpuCard:
                    # 引き分け
                    resultText = '結果は引き分けです。'
                elif playerCard > cpuCard:
                    # プレイヤーの勝ち
                    resultText = 'プレイヤーの勝ちです。'
                else:
                    # CPUの勝ち
                    resultText = 'CPUの勝ちです。'
                # 結果モーダル
                self.modal = Factory.SixSecoundResultModal()
                if self.turn == 1:
                    self.modal.turnLabelText = 'あなたは' + str(cardNum) + 'を出しました。'
                else:
                    self.modal.turnLabelText = 'CPUは' + str(cardNum) + 'を出しました。'
                self.modal.resultLabelText = 'プレイヤーの手札は' + str(playerCard) + '。' + 'CPUの手札は' + str(cpuCard) + '。' + resultText
                self.modal.open()
                returnFlg = 1
            else:
                # 1枚目の場合
                self.modal = Factory.SixFirstResultModal()
                if self.turn == 1:
                    self.modal.turnLabelText = 'あなたは' + str(cardNum) + 'を出しました。'
                else:
                    self.modal.turnLabelText = 'CPUは' + str(cardNum) + 'を出しました。'
                self.modal.resultPlayerLabelText = 'プレイヤーの手札は' + str(playerCard)
                self.modal.resultCpuLabelText = 'CPUの手札は' + str(cpuCard)
                self.modal.open()
                returnFlg = 0
             
            return returnFlg

        # 7のカードを出す処理
        def sevenEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            self.modal.open()
            return 0

        # 8のカードを出す処理
        def eightEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            # プレイヤーとCPUのカードを交換
            playerCard = self.playerHandList[0]
            cpuCard = self.cpuHandList[0]
            self.playerHandList[0] = cpuCard
            self.cpuHandList[0] = playerCard
            self.modal.open()
            return 0

        # 9のカードを出す処理
        def nineEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                self.modal.add_widget(Factory.Label(text='あなたは' + str(cardNum) + 'を出しました。'))
            else:
                self.modal.add_widget(Factory.Label(text='CPUは' + str(cardNum) + 'を出しました。'))
            self.modal.open()
            return 0

        # カード効果発動処理本体
        endFlg = 0
        if 1 == cardNum :
            endFlg = oneEfficacy(self)
        elif 2 == cardNum :
            endFlg = twoEfficacy(self)
        elif 3 == cardNum :
            endFlg = threeEfficacy(self)
        elif 4 == cardNum :
            endFlg = fourEfficacy(self)
        elif 5 == cardNum :
            endFlg = fiveEfficacy(self)
        elif 6 == cardNum :
            endFlg = sixfficacy(self)
        elif 7 == cardNum :
            endFlg = sevenEfficacy(self)
        elif 8 == cardNum :
            endFlg = eightEfficacy(self)
        elif 9 == cardNum :
            endFlg = nineEfficacy(self)
        return endFlg

    # 画面を更新する
    def refresh(self):
        # プレイヤーの手札を更新
        self.ids.playerHandBox.clear_widgets()
        for cardNum in self.playerHandList:
            cardImage = Factory.CardImage(source=self.cardDict[cardNum].image )
            cardImage.num = cardNum
            cardImage.card = self.cardDict[cardNum]
            cardImage.playCardButtonDispFlg =  1 if cardNum != 10 else 0#True
            self.ids.playerHandBox.add_widget(cardImage)
        # プレイヤーの捨て札を更新
        self.ids.playerDiscardBox.clear_widgets()
        for cardNum in self.playerDiscardList:
            cardImage = Factory.CardImage(source=self.cardDict[cardNum].image )
            cardImage.num = cardNum
            cardImage.card = self.cardDict[cardNum]
            self.ids.playerDiscardBox.add_widget(cardImage)
        # cpuの手札を更新
        self.ids.cpuHandBox.clear_widgets()
        for cardNum in self.cpuHandList:
            self.ids.cpuHandBox.add_widget(Factory.CardImage())
        # cpuの捨て札を更新
        self.ids.cpuDiscardBox.clear_widgets()
        for cardNum in self.cpuDiscardList:
            cardImage = Factory.CardImage(source=self.cardDict[cardNum].image )
            cardImage.num = cardNum
            cardImage.card = self.cardDict[cardNum]
            self.ids.cpuDiscardBox.add_widget(cardImage)
        pass
    pass

# 先攻後攻選択画面
class SelectTurn(Factory.FloatLayout):
    def setFirstStrike(self):
        App.get_running_app().root.gotoInit(1)
    def setSecondStrike(self):
        App.get_running_app().root.gotoInit(2)
    pass

# 画面切替ウィジェット
class XenoRootWidget(Factory.FloatLayout):
    # タイトル画面へ
    def gotoTitle(self):
        self.clear_widgets()
        self.add_widget(Factory.TitleWidget())
    # 先攻後攻選択画面へ
    def gotoSelectTurn(self):
        self.clear_widgets()
        self.add_widget(Factory.SelectTurn())
    # メイン画面へ
    def gotoInit(self, turn):
        self.clear_widgets()
        self.add_widget(Factory.XenoMainWidget(turn=turn))
        pass
    pass

class XenoApp(App):
    def build(self):
        self.title = 'XENO'
        self.icon = 'icon.ico'
        self.root = XenoRootWidget()
        self.root.gotoTitle()
        return self.root

if __name__ == '__main__':
    XenoApp().run()
