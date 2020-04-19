# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout

import japanize_kivy

class SelectTurn(FloatLayout):
    def setFirstStrike(self):
        # ロジックの初期設定
        self.playerTurn = 1
    def setSecondStrike(self):
        # ロジックの初期設定
        self.playerTurn = 2
    pass

class RootWidget(FloatLayout):
    def gotoTitle(self):
        self.clear_widgets()
        self.add_widget(Factory.TitleWidget())
    def gotoSelectTurn(self):
        self.clear_widgets()
        self.add_widget(Factory.SelectTurn())
    pass

class ScreenTransitionApp(App):
    def build(self):
        self.title = 'XENO'
        root = RootWidget()
        root.gotoTitle()
        return root

if __name__ == '__main__':
    ScreenTransitionApp().run()
