# -*- coding: utf-8 -*-
import japanize_kivy, sys, random
sys.dont_write_bytecode = True

from kivy.app import App
from kivy.core.window import Window
Window.size = (480, 720)

from kivy.factory import Factory

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

        # cpu処理
        xenoMainWidget.cpuTurnLogic()     
        pass

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # デッキを作成する
        self.deck = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,10]
        random.shuffle(self.deck)

        # デッキの一番下のカードを転生札に設定する
        self.reincarnationCard = self.deck.pop(-1)

        # 手札を配る
        self.playerHandList.append(self.deck.pop(0))
        self.cpuHandList.append(self.deck.pop(0))

        # ドローする
        self.drawDeck()
        
        # 画面更新
        self.refresh()
        pass

    # デッキから1枚ドローする
    def drawDeck(self):
        # デッキがドローできるか確認
        if len(self.deck) == 0:
            return
        # ターンの確認
        if self.turn == 1:
            # プレイヤーのターン
            self.playerHandList.append(self.deck.pop(0))
        else:
            # cpuのターン
            self.cpuHandList.append(self.deck.pop(0))
        pass

    # CPUのターン処理
    def cpuTurnLogic(self):
        # ターンフラグをcpuにする
        self.turn = 2
        # ドローする
        self.drawDeck()
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
        cardNum = self.cpuHandList[random.randint(0,1)]
        # カードが手札に含まれているか確認
        if not cardNum in self.cpuHandList:
            return
        # 手札から捨て札にカードを出す
        self.cpuHandList.pop(self.cpuHandList.index(cardNum))
        self.cpuDiscardList.append(cardNum)
        # 画面更新
        self.refresh() 
        pass

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
class XenoRootWidget(Factory.FloatLayout):
    def gotoInit(self):
        self.clear_widgets()
        self.add_widget(Factory.XenoMainWidget())
        pass
    pass

class XenoApp(App):
    def build(self):
        self.title = 'XENO'
        root = XenoRootWidget()
        root.gotoInit()
        return root

if __name__ == '__main__':
    XenoApp().run()
