# -*- coding: utf-8 -*-
import japanize_kivy
import sys
sys.dont_write_bytecode = True

from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout

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