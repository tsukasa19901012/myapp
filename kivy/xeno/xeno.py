# -*- coding: utf-8 -*-
import sys, random
sys.dont_write_bytecode = True
import types
from kivy.clock import Clock
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
LabelBase.register(DEFAULT_FONT, "ipaexg.ttf")
from kivy.app import App
from kivy.core.window import Window
Window.size = (480, 720)
from dataclasses import dataclass
from kivy.factory import Factory

# 処理一時停止のための機能
def start_coro(coro):
    def step_coro(*args, **kwargs):
        try:
            coro.send((args, kwargs, ))(step_coro)
        except StopIteration:
            pass
    try:
        coro.send(None)(step_coro)
    except StopIteration:
        pass
async def thread(func, *args, **kwargs):
    from threading import Thread
    return_value = None
    is_finished = False
    def wrapper(*args, **kwargs):
        nonlocal return_value, is_finished
        return_value = func(*args, **kwargs)
        is_finished = True
    Thread(target=wrapper, args=args, kwargs=kwargs).start()
    while not is_finished:
        await sleep(3)
    return return_value
@types.coroutine
def sleep(duration):
    args, kwargs = yield lambda step_coro: Clock.schedule_once(step_coro, duration)
    return args[0]
@types.coroutine
def event(ed, name):
    bind_id = None
    step_coro = None
    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = ed.fbind(name, callback)
        assert bind_id > 0  # bindingに成功したか確認
        step_coro = step_coro_
    def callback(*args, **kwargs):
        ed.unbind_uid(name, bind_id)
        step_coro(*args, **kwargs)
    return (yield bind)

# カード情報クラス
@dataclass
class Card:
    rank: str = '' # カードランク
    name: str = ''# カード名
    efficacy: str = '' # カード効果
    efficacyContent: str = '' # カード効果内容
    image: str = '' # カード画像

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
        start_coro(self.playCardButtonLogic(obj))

    async def playCardButtonLogic(self, obj):
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
        await sleep(0.5)
        # カード効果発動
        endFlg = await xenoMainWidget.activationCardEffect(cardNum)
        # ゲーム終了か確認
        if endFlg == 1:
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # デッキがない場合
        if len(xenoMainWidget.deck) == 0:
            # 手札カードの比較を行う
            await xenoMainWidget.lastConfrontation()
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # cpu処理
        await sleep(0.5)
        await xenoMainWidget.cpuTurnLogic()

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

    # ログ
    def outputLog(self):
        print('　デッキ',len(self.deck),'枚：',self.deck)
        print('　転生札', self.reincarnationCard)
        print('　プレイヤー手札：', self.playerHandList)
        print('　プレイヤー捨て札：', self.playerDiscardList)
        print('　CPU手札：', self.cpuHandList)
        print('　CPU捨て札：', self.cpuDiscardList)
        print('　プレイヤー守護フラグ：', self.playerFourFlg)
        print('　プレイヤー賢者フラグ：', self.playerSevenFlg)
        print('　CPU守護フラグ：', self.cpuFourFlg)
        print('　CPU賢者フラグ：', self.cpuSevenFlg)
        allCnt = len(self.deck) + len(self.playerHandList) + len(self.playerDiscardList) + len(self.cpuHandList) + len(self.cpuDiscardList)
        if self.reincarnationCard != 0:
            allCnt = allCnt + 1
        if allCnt == 18:
            print('　カード枚数OK')
        else:
            print('　!!!!!!!!!!!!! カード枚数NG ', allCnt, '!!!!!!!!!!!!!')

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

        # ログ
        print('ゲーム準備完了')
        self.outputLog()

        # 1ターン目の処理
        endFlg = start_coro(self.oneTurnLogic())
        # ゲーム終了か確認
        if endFlg == 1:
            # タイトルに戻る
            root = App.get_running_app().root
            root.gotoTitle()

        # 画面更新
        self.refresh()
        pass

    # 1ターン目の処理
    async def oneTurnLogic(self):
        await sleep(0.5)
        if self.turn == 1 :
            print('プレイヤーのターンです。')
            return await self.drawDeck()
        else:
            print('CPUのターンです。')
            return await self.cpuTurnLogic()

    # デッキから1枚ドローする
    async def drawDeck(self):
        class ImageButton(Factory.ButtonBehavior, Factory.Image):  
            # 7の効果のカード選択処理
            def on_press(self):
                xenoMainWidget = App.get_running_app().root.children[0]
                # 選択したカード位置
                selectIndex = self.drawList.index(self.num)
                for index, card in  enumerate(self.drawList):
                    if index == selectIndex:
                        # 選択したカードは手札に追加
                        print('　7で選択したカード', card)
                        xenoMainWidget.playerHandList.append(card)
                    else:
                        # それ以外は山札に戻す
                        xenoMainWidget.deck.append(card)
                # デッキをシャッフルする
                random.shuffle(xenoMainWidget.deck)
                # モーダルを閉じる
                xenoMainWidget.modal.dismiss()
                xenoMainWidget.outputLog()

        # プレイヤーのターン
        if self.turn == 1:
            # 7のカード効果
            if self.playerSevenFlg == 1:
                print('プレイヤーが7の効果を発動')
                deckCnt = len(self.deck)
                # 3枚までドロー(デッキが3枚より少ない場合はデッキ枚数)
                drawList = []
                for i in range(deckCnt):
                    if i > 2 :
                        break
                    drawList.append(self.deck.pop(0))
                print('　7の効果で引いたカード:', drawList)
                # 引いたカードをboxLayoutで作る
                cardBox = Factory.BoxLayout(orientation='horizontal')
                for index, card in  enumerate(drawList):
                    image = Factory.ImageButton(source=self.cardDict[card].image)
                    image.num = card
                    image.drawList = drawList
                    cardBox.add_widget(image)
                # 表示モーダル
                self.modal = Factory.BasicEfficacySelectModal()
                self.modal.resultLabelText = '7の効果です。手札に加える1枚を選んでください。'
                self.modal.ids.box.add_widget(cardBox)
                self.modal.open()
                await event(self.modal, 'on_dismiss')
            # 通常のドロー
            else:
                print('プレイヤードロー')
                self.playerHandList.append(self.deck.pop(0))
                self.outputLog()
            # 7のカード効果フラグを0に戻す
            self.playerSevenFlg = 0
        # cpuのターン
        else:
            # 7のカード効果
            if self.cpuSevenFlg == 1:
                print('CPUが7の効果を発動')
                deckCnt = len(self.deck)
                # 3枚までドロー(デッキが3枚より少ない場合はデッキ枚数)
                drawList = []
                for i in range(deckCnt):
                    if i > 2 :
                        break
                    drawList.append(self.deck.pop(0))
                print('　7の効果で引いたカード:', drawList)
                # 1番大きいカードを選ぶ
                selectIndex = 0
                selectCardNum = 0
                for index, card in  enumerate(drawList):
                    if card > selectCardNum:
                        selectCardNum = card
                        selectIndex = index
                # 7のカード効果選択後処理
                for index, card in  enumerate(drawList):
                    if index == selectIndex:
                        # 選択したカードは手札に追加
                        print('　7で選択したカード', card)
                        self.cpuHandList.append(card)
                    else:
                        # それ以外は山札に戻す
                        self.deck.append(card)
                # デッキをシャッフルする
                random.shuffle(self.deck)
                self.outputLog()
            # 通常のドロー
            else:
                print('CPUドロー')
                self.cpuHandList.append(self.deck.pop(0))
                self.outputLog()
            # 7のカード効果フラグを0に戻す
            self.cpuSevenFlg = 0
        # 画面更新
        self.refresh()
        return 0

    # CPUのターン処理
    async def cpuTurnLogic(self):
        # デッキがない場合
        if len(self.deck) == 0:
            # 対決を行う
            await self.lastConfrontation()
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # ターンフラグをcpuにする
        self.turn = 2
        # ドローする
        await self.drawDeck()
        # 画面更新
        self.refresh()
        await sleep(0.5)
        # cpuがカードを出す
        endFlg = await self.cpuPlayCard()
        # ゲーム終了か確認
        if endFlg == 1:
            # タイトルに戻る
            root = App.get_running_app().root
            root.gotoTitle()
        # デッキがない場合
        if len(self.deck) == 0:
            # 対決を行う
            await self.lastConfrontation()
            # タイトルに戻る
            root = App.get_running_app().root
            return root.gotoTitle()
        # プレイヤーにドローさせる。
        self.turn = 1
        await self.drawDeck()
        # 画面更新
        self.refresh() 
        pass

    # cpuがカードを出す
    async def cpuPlayCard(self):
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
        await sleep(0.5)
        # カード効果発動
        endFlg = await self.activationCardEffect(cardNum)
        # ゲーム終了か確認
        if endFlg == 1:
            return 1
        # 画面更新
        self.refresh() 
        await sleep(0.5)
        return 0

    # デッキがない場合の対決処理
    async def lastConfrontation(self):
        # 互いの手札を取得
        playerCard = self.playerHandList[0]
        cpuCard = self.cpuHandList[0]
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
        self.modal.turnLabelText = '山札がないため手札の比較をします。'
        self.modal.resultLabelText = 'プレイヤーの手札は' + str(playerCard) + '。' + 'CPUの手札は' + str(cpuCard) + '。' + resultText
        self.modal.open()
        await event(self.modal, 'on_dismiss')

    # カード効果発動
    async def activationCardEffect(self, cardNum):
        # 1のカードを出す処理
        async def oneEfficacy(self):
            self.selectCard = 0
            class ImageButton(Factory.ButtonBehavior, Factory.Image):  
                # 1の効果のカード選択処理
                def on_press(self):
                    xenoMainWidget = App.get_running_app().root.children[0]
                    xenoMainWidget.selectCard = self.num
                    # 選択したカード位置
                    selectIndex = xenoMainWidget.cpuHandList.index(self.num)
                    for index, card in  enumerate(xenoMainWidget.cpuHandList):
                        if index == selectIndex:
                            # 選択したカードは捨て札に追加
                            print('　1で選択したカード', card)
                            xenoMainWidget.cpuDiscardList.append(xenoMainWidget.cpuHandList.pop(selectIndex))
                    # デッキをシャッフルする
                    random.shuffle(xenoMainWidget.deck)
                    xenoMainWidget.refresh()
                    # モーダルを閉じる
                    xenoMainWidget.modal.dismiss()

            # 1枚目の場合
            if 1 == self.playerDiscardList.count(1) + self.cpuDiscardList.count(1) :
                self.modal = Factory.BasicEfficacyModal()
                # プレイヤーのターン
                if self.turn == 1:
                    print('プレイヤーが1を出す(1枚目)')
                    self.modal.resultLabelText = 'あなたは' + str(1) + 'を出しました。'
                # CPUのターン
                else:
                    print('CPUが1を出す(1枚目)')
                    self.modal.resultLabelText = 'CPUは' + str(1) + 'を出しました。'
                self.modal.open()
                await event(self.modal, 'on_dismiss')
            # 2枚目の場合
            else:
                # プレイヤーのターン
                if self.turn == 1:
                    print('プレイヤーが1を出す(2枚目)')
                    # CPUが守護の場合
                    if self.cpuFourFlg == 1:
                        self.modal.resultLabelText = 'あなたは' + str(1) + 'を出しましたが、\n守護されました。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                    # CPUが守護でない場合
                    else:
                        self.modal = Factory.BasicEfficacySelectModal()
                        self.modal.resultLabelText = 'あなたは' + str(1) + 'を出しました。'
                        # デッキがあれば、1の効果での選択
                        if len(self.deck) != 0:
                            self.modal.ids.box.add_widget(Factory.Label(text='捨て札にするカードを選択してください', size_hint_y=0.2))
                            self.cpuHandList.append(self.deck.pop(0))
                            # CPUの手札でをboxLayoutで作る
                            cardBox = Factory.BoxLayout(orientation='horizontal')
                            for index, card in  enumerate(self.cpuHandList):
                                image = ImageButton(source=self.cardDict[card].image)
                                image.num = card
                                cardBox.add_widget(image)
                            self.modal.ids.box.add_widget(cardBox)
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        # カードが10の場合
                        if self.selectCard == 10:
                            self.modal = Factory.BasicEfficacyModal()
                            self.modal.resultLabelText = 'CPUは転生します。'
                            self.modal.open()
                            await event(self.modal, 'on_dismiss')
                            await sleep(0.5)
                            # CPUは手札を捨てる
                            self.cpuDiscardList.append(self.cpuHandList.pop(0))
                            self.refresh()
                            await sleep(0.5)
                            # CPUは転生札を手札にする
                            self.cpuHandList.append(self.reincarnationCard)
                            self.reincarnationCard = 0
                            self.refresh()
                            await sleep(0.5)
                # CPUのターン
                else:
                    print('CPUが1を出す(2枚目)')
                    # プレイヤーが守護の場合
                    if self.playerFourFlg == 1:
                        self.modal.resultLabelText = 'CPUは' + str(1) + 'を出しましたが、\n守護されました。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                    # プレイヤーが守護でない場合
                    else:
                        self.modal = Factory.BasicEfficacyModal()
                        self.modal.resultLabelText = 'CPUは' + str(1) + 'を出しました。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        # デッキがあれば、1の効果での選択
                        if len(self.deck) != 0:
                            self.playerHandList.append(self.deck.pop(0))
                            self.refresh()
                            await sleep(0.5)
                            # 1番大きいカードを選ぶ
                            selectIndex = 0
                            selectCardNum = 0
                            for index, card in  enumerate(self.playerHandList):
                                if card > selectCardNum:
                                    selectCardNum = card
                                    selectIndex = index
                            # 1の効果選択後処理
                            self.selectCard = selectCardNum
                            for index, card in  enumerate(self.playerHandList):
                                if index == selectIndex:
                                    # 選択したカードは捨て札
                                    print('　1で選択したカード', card)
                                    self.playerDiscardList.append(self.playerHandList.pop(selectIndex))
                        self.refresh()
                        await sleep(0.5)
                        # カードが10の場合
                        if self.selectCard == 10:
                            self.modal = Factory.BasicEfficacyModal()
                            self.modal.resultLabelText = 'プレイヤーは転生します。'
                            self.modal.open()
                            await event(self.modal, 'on_dismiss')
                            await sleep(0.5)
                            # プレイヤーは手札を捨てる
                            self.playerDiscardList.append(self.playerHandList.pop(0))
                            self.refresh()
                            await sleep(0.5)
                            # プレイヤーは転生札を手札にする
                            self.playerHandList.append(self.reincarnationCard)
                            self.reincarnationCard = 0
                            self.refresh()
                            await sleep(0.5)
            return 0

        # 2のカードの出す処理
        async def twoEfficacy(self):
            returnFlg = 0
            self.selectCard = 0
            def press_Button(button):
                self.selectCard = button.value
                self.modal.dismiss()
            # プレイヤーのターン
            if self.turn == 1:
                print('プレイヤーが2を出す')
                # CPUが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'あなたは' + str(2) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # CPUが守護でない場合
                else:
                    self.modal = Factory.BasicEfficacySelectModal()
                    self.modal.resultLabelText = 'あなたは' + str(2) + 'を出しました。'
            # CPUのターン
            else:
                print('CPUが2を出す')
                # プレイヤーが守護の場合
                if self.playerFourFlg == 1:
                    self.modal.resultLabelText = 'CPUは' + str(2) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # プレイヤーが守護でない場合
                else:
                    self.modal = Factory.BasicEfficacyModal()
                    self.modal.resultLabelText = 'CPUは' + str(2) + 'を出しました。'
            # 2の効果での選択
            if self.turn == 1:
                self.modal.ids.box.add_widget(Factory.Label(text='予想するカードを選択してください', size_hint_y=0.2))
                gridLayout = Factory.GridLayout(cols=5)
                gridLayout.size_hint_y = 0.6
                gridLayout.spacing = [10, 10]
                for i in range(1, 11):
                    button = Factory.Button(text=str(i))
                    button.value = i
                    button.bind(on_press=press_Button)
                    gridLayout.add_widget(button)
                self.modal.ids.box.add_widget(gridLayout)
                self.modal.open()
                await event(self.modal, 'on_dismiss')
            else:
                # ランダムで1-10のカードを選択する。
                self.selectCard = random.randint(1,10)
                self.modal.ids.box.add_widget(Factory.Label(text='CPUが予想したカードは' + str(self.selectCard) + 'です。'))
                self.modal.open()
                await event(self.modal, 'on_dismiss')
            # 2の効果の結果
            print('　予想したカード　', self.selectCard)
            self.modal = Factory.BasicEfficacyModal()
            # プレイヤーのターン
            if self.turn == 1:
                cpuCard = self.cpuHandList[0]
                # 予想が当たる
                if self.selectCard == cpuCard:
                    # カードが10の場合
                    if self.selectCard == 10:
                        self.modal.resultLabelText = '予想が当たりましたが、CPUは転生します。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        await sleep(0.5)
                        # CPUは手札を捨てる
                        self.cpuDiscardList.append(self.cpuHandList.pop(0))
                        self.refresh()
                        await sleep(0.5)
                        # CPUは転生札を手札にする
                        self.cpuHandList.append(self.reincarnationCard)
                        self.reincarnationCard = 0
                        self.refresh()
                        await sleep(0.5)
                    # カードが10以外の場合
                    else:
                        self.modal.resultLabelText = '予想が当たりました。プレイヤーの勝ちです。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        returnFlg = 1
                # 予想が外れる
                else:
                    self.modal.resultLabelText = '予想が外れました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
            # CPUのターン
            else:
                playerCard = self.playerHandList[0]
                # 予想が当たる
                if self.selectCard == playerCard:
                    # カードが10の場合
                    if self.selectCard == 10:
                        self.modal.resultLabelText = '予想が当たりましたが、プレイヤーは転生します。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        await sleep(0.5)
                        # プレイヤーは手札を捨てる
                        self.playerDiscardList.append(self.playerHandList.pop(0))
                        self.refresh()
                        await sleep(0.5)
                        # プレイヤーは転生札を手札にする
                        self.playerHandList.append(self.reincarnationCard)
                        self.reincarnationCard = 0
                        self.refresh()
                        await sleep(0.5)
                    # カードが10以外の場合
                    else:
                        self.modal.resultLabelText = '予想が当たりました。CPUの勝ちです。'
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        returnFlg = 1
                # 予想が外れる
                else:
                    self.modal.resultLabelText = '予想が外れました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
           
            return returnFlg

        # 3のカードを出す処理
        async def threeEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                print('プレイヤーが3を出す')
                # CPUが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'あなたは' + str(3) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # CPUが守護でない場合
                else:
                    self.modal.resultLabelText = 'あなたは' + str(3) + 'を出しました。'
                    cpuCard = self.cpuHandList[0]
                    self.modal.ids.box.add_widget(Factory.Label(text='CPUの手札は' + str(cpuCard) + 'です。'))
            else:
                print('CPUが3を出す')
                # プレイヤーが守護の場合
                if self.playerFourFlg == 1:
                    self.modal.resultLabelText = 'CPUは' + str(3) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # プレイヤーが守護でない場合
                else:
                    self.modal.resultLabelText = 'CPUは' + str(3) + 'を出しました。'
                    playerCard = self.playerHandList[0]
                    self.modal.ids.box.add_widget(Factory.Label(text='プレイヤーの手札は' + str(playerCard) + 'です。'))
            self.modal.open()
            await event(self.modal, 'on_dismiss')
            return 0

        # 4のカードを出す処理
        async def fourEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                print('プレイヤーが4を出す')
                self.modal.resultLabelText = 'あなたは' + str(4) + 'を出しました。'
                self.playerFourFlg = 1
            else:
                print('CPUが4を出す')
                self.modal.resultLabelText = 'CPUは' + str(4) + 'を出しました。'
                self.cpuFourFlg = 1
            self.modal.open()
            await event(self.modal, 'on_dismiss')
            return 0

        # 5のカードを出す処理
        async def fiveEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                print('プレイヤーが5を出す')
                # CPUが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'あなたは' + str(5) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # CPUが守護でない場合
                else:
                    self.modal.resultLabelText = 'あなたは' + str(5) + 'を出しました。'
            else:
                print('CPUが5を出す')
                # プレイヤーが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'CPUは' + str(5) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # プレイヤーが守護でない場合
                else:
                    self.modal.resultLabelText = 'CPUは' + str(5) + 'を出しました。'
            self.modal.open()
            await event(self.modal, 'on_dismiss')

            # デッキがあれば、5の効果処理を行う
            if len(self.deck) != 0:
                discardCardNum = 0
                if self.turn == 1:
                    # CPUにドローさせる
                    self.cpuHandList.append(self.deck.pop(0))
                    self.refresh() 
                    await sleep(0.5)
                    # ランダムで1枚捨てる
                    discardCardNum = self.cpuHandList[random.randint(0,1)]
                    self.cpuHandList.pop(self.cpuHandList.index(discardCardNum))
                    self.cpuDiscardList.append(discardCardNum)
                else:
                    # プレイヤーにドローさせる
                    self.playerHandList.append(self.deck.pop(0))
                    self.refresh() 
                    await sleep(0.5)
                    # ランダムで1枚捨てる
                    discardCardNum = self.playerHandList[random.randint(0,1)]
                    self.playerHandList.pop(self.playerHandList.index(discardCardNum))
                    self.playerDiscardList.append(discardCardNum)
                self.refresh() 
                await sleep(0.5)

                # 捨てたカードが10の場合、転生を行う
                if 10 == discardCardNum:
                    if self.turn == 1:
                        # CPUは手札を捨てる
                        self.cpuDiscardList.append(self.cpuHandList.pop(0))
                        self.refresh()
                        await sleep(0.5)
                        # CPUは転生札を手札にする
                        self.cpuHandList.append(self.reincarnationCard)
                    else:
                        # プレイヤーは手札を捨てる
                        self.playerDiscardList.append(self.playerHandList.pop(0))
                        self.refresh()
                        await sleep(0.5)
                        # プレイヤーは転生札を手札にする
                        self.playerHandList.append(self.reincarnationCard)
                    self.reincarnationCard = 0
                    self.refresh() 
                    await sleep(0.5)
            return 0

        # 6のカードを出す処理
        async def sixEfficacy(self):
            # プレイヤーのターン
            if self.turn == 1:
                print('プレイヤーが6を出す')
                # CPUが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'あなたは' + str(6) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
            # CPUのターン
            else:
                print('CPUが6を出す')
                # プレイヤーが守護の場合
                if self.playerFourFlg == 1:
                    self.modal.resultLabelText = 'CPUは' + str(6) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
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
                    self.modal.turnLabelText = 'あなたは' + str(6) + 'を出しました。'
                else:
                    self.modal.turnLabelText = 'CPUは' + str(6) + 'を出しました。'
                self.modal.resultLabelText = 'プレイヤーの手札は' + str(playerCard) + '。' + 'CPUの手札は' + str(cpuCard) + '。' + resultText
                self.modal.open()
                await event(self.modal, 'on_dismiss')
                returnFlg = 1
            else:
                # 1枚目の場合
                self.modal = Factory.SixFirstResultModal()
                if self.turn == 1:
                    self.modal.turnLabelText = 'あなたは' + str(6) + 'を出しました。'
                else:
                    self.modal.turnLabelText = 'CPUは' + str(6) + 'を出しました。'
                self.modal.resultPlayerLabelText = 'プレイヤーの手札は' + str(playerCard)
                self.modal.resultCpuLabelText = 'CPUの手札は' + str(cpuCard)
                self.modal.open()
                await event(self.modal, 'on_dismiss')
                returnFlg = 0
             
            return returnFlg

        # 7のカードを出す処理
        async def sevenEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                print('プレイヤーが7を出す')
                self.modal.resultLabelText = 'あなたは' + str(7) + 'を出しました。'
                self.playerSevenFlg = 1
            else:
                self.modal.resultLabelText = 'CPUは' + str(7) + 'を出しました。'
                self.cpuSevenFlg = 1
            self.modal.open()
            await event(self.modal, 'on_dismiss')
            return 0

        # 8のカードを出す処理
        async def eightEfficacy(self):
            self.modal = Factory.BasicEfficacyModal()
            if self.turn == 1:
                print('プレイヤーが8を出す')
                # CPUが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'あなたは' + str(8) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # CPUが守護でない場合
                else:
                    self.modal.resultLabelText = 'あなたは' + str(8) + 'を出しました。'
            else:
                print('CPUが8を出す')
                # プレイヤーが守護の場合
                if self.playerFourFlg == 1:
                    self.modal.resultLabelText = 'CPUは' + str(8) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # プレイヤーが守護でない場合
                else:
                    self.modal.resultLabelText = 'CPUは' + str(8) + 'を出しました。'
            self.modal.ids.box.add_widget(Factory.Label(text='手札を交換します。'))
            # プレイヤーとCPUのカードを交換
            playerCard = self.playerHandList[0]
            cpuCard = self.cpuHandList[0]
            self.playerHandList[0] = cpuCard
            self.cpuHandList[0] = playerCard
            self.modal.open()
            await event(self.modal, 'on_dismiss')
            self.refresh() 
            await sleep(0.5)
            return 0

        # 9のカードを出す処理
        async def nineEfficacy(self):
            returnFlg = 0
            self.selectCard = 0
            class ImageButton(Factory.ButtonBehavior, Factory.Image):  
                # 9の効果のカード選択処理
                def on_press(self):
                    xenoMainWidget = App.get_running_app().root.children[0]
                    xenoMainWidget.selectCard = self.num
                    # 選択したカード位置
                    selectIndex = xenoMainWidget.cpuHandList.index(self.num)
                    for index, card in  enumerate(xenoMainWidget.cpuHandList):
                        if index == selectIndex:
                            # 選択したカードは捨て札に追加
                            print('　9で選択したカード', card)
                            xenoMainWidget.cpuDiscardList.append(xenoMainWidget.cpuHandList.pop(selectIndex))
                    # デッキをシャッフルする
                    random.shuffle(xenoMainWidget.deck)
                    xenoMainWidget.refresh()
                    # モーダルを閉じる
                    xenoMainWidget.modal.dismiss()

            if self.turn == 1:
                print('プレイヤーが9を出す')
                # CPUが守護の場合
                if self.cpuFourFlg == 1:
                    self.modal.resultLabelText = 'あなたは' + str(1) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    return 0
                # CPUが守護でない場合
                else:
                    self.modal = Factory.BasicEfficacySelectModal()
                    self.modal.resultLabelText = 'あなたは' + str(9) + 'を出しました。'
                    # デッキがあれば、9の効果での選択
                    if len(self.deck) != 0:
                        self.modal.ids.box.add_widget(Factory.Label(text='捨て札にするカードを選択してください', size_hint_y=0.2))
                        self.cpuHandList.append(self.deck.pop(0))
                        # CPUの手札でをboxLayoutで作る
                        cardBox = Factory.BoxLayout(orientation='horizontal')
                        for index, card in  enumerate(self.cpuHandList):
                            image = ImageButton(source=self.cardDict[card].image)
                            image.num = card
                            cardBox.add_widget(image)
                        self.modal.ids.box.add_widget(cardBox)
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    # カードが10の場合
                    if self.selectCard == 10:
                        self.modal = Factory.BasicEfficacyModal()
                        self.modal.resultLabelText = '「英雄」を公開処刑したため、プレイヤーの勝ちです。'
                        returnFlg = 1
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        await sleep(0.5)
            else:
                print('CPUが9を出す')
                # プレイヤーが守護の場合
                if self.playerFourFlg == 1:
                    self.modal.resultLabelText = 'CPUは' + str(1) + 'を出しましたが、\n守護されました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                # プレイヤーが守護でない場合
                else:
                    self.modal = Factory.BasicEfficacyModal()
                    self.modal.resultLabelText = 'CPUは' + str(9) + 'を出しました。'
                    self.modal.open()
                    await event(self.modal, 'on_dismiss')
                    # デッキがあれば、9の効果での選択
                    if len(self.deck) != 0:
                        self.playerHandList.append(self.deck.pop(0))
                        self.refresh()
                        await sleep(0.5)
                        # 1番大きいカードを選ぶ
                        selectIndex = 0
                        selectCardNum = 0
                        for index, card in  enumerate(self.playerHandList):
                            if card > selectCardNum:
                                selectCardNum = card
                                selectIndex = index
                        # 9の効果選択後処理
                        self.selectCard = selectCardNum
                        for index, card in  enumerate(self.playerHandList):
                            if index == selectIndex:
                                # 選択したカードは捨て札
                                print('　9で選択したカード', card)
                                self.playerDiscardList.append(self.playerHandList.pop(selectIndex))
                    self.refresh()
                    await sleep(0.5)
                    # カードが10の場合
                    if self.selectCard == 10:
                        self.modal = Factory.BasicEfficacyModal()
                        self.modal.resultLabelText = '「英雄」を公開処刑したため、CPUの勝ちです。'
                        returnFlg = 1
                        self.modal.open()
                        await event(self.modal, 'on_dismiss')
                        await sleep(0.5)
            return returnFlg

        # カード効果発動処理本体
        endFlg = 0
        if 1 == cardNum :
            endFlg = await oneEfficacy(self)
        elif 2 == cardNum :
            endFlg = await twoEfficacy(self)
        elif 3 == cardNum :
            endFlg = await threeEfficacy(self)
        elif 4 == cardNum :
            endFlg = await fourEfficacy(self)
        elif 5 == cardNum :
            endFlg = await fiveEfficacy(self)
        elif 6 == cardNum :
            endFlg = await sixEfficacy(self)
        elif 7 == cardNum :
            endFlg = await sevenEfficacy(self)
        elif 8 == cardNum :
            endFlg = await eightEfficacy(self)
        elif 9 == cardNum :
            endFlg = await nineEfficacy(self)
        
        # 守護フラグをリセット
        if self.turn == 1:
            self.cpuFourFlg = 0
        else:
            self.playerFourFlg = 0

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
