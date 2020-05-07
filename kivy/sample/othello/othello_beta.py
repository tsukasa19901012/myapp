# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import ObjectProperty
from kivy.lang import Builder
import numpy as np
import sys

import othello_alpha
from othello_alpha import Player, Computer, setField

Builder.load_file('othello_beta.kv')

class BtnReturn(Button):
    def __init__(self, **kwargs):
        super(BtnReturn, self).__init__(**kwargs)
        self.background_color = [0.28125, 0.36328, 0.24609, 1]
        self.background_normal = ''
        self.color = [1, 1, 1, 1]
        self.font_size = 36
        self.size_hint = [0.6, 0.2]
        self.text = 'Return'
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.canvas.before.clear()
        self.canvas.before.add(Color(rgb=[0, 0, 0]))
        self.canvas.before.add(Line(rectangle=[self.x, self.y, self.width, self.height], width=5))
    def on_press(self):
        othello_alpha.field = setField()
        app = App.get_running_app()
        app.root.gotoTitle()
    pass

class TurnLabel(Label):
    def __init__(self, **kwargs):
        super(TurnLabel, self).__init__(**kwargs)
        self.bold = True
        self.color = [0, 0, 0, 1]
        self.font_size = 26
        self.text = ''
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.text_size = [self.width*0.8, 50]
    pass

class CountWidget(GridLayout):
    def __init__(self, **kwargs):
        super(CountWidget, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 3
        self.size_hint = [0.8, 0.6]
        if(othello_alpha.playerStone == 1):
            self.add_widget(Label(text='You', color=[1, 1, 1, 1], font_size=26, bold=True))
            self.add_widget(Label(text='Computer', color=[1, 1, 1, 1], font_size=26, bold=True))
        elif(othello_alpha.playerStone == 2):
            self.add_widget(Label(text='Computer', color=[1, 1, 1, 1], font_size=26, bold=True))
            self.add_widget(Label(text='You', color=[1, 1, 1, 1], font_size=26, bold=True))
        self.add_widget(Label(text='Black', color=[1, 1, 1, 1], font_size=26, bold=True))
        self.add_widget(Label(text='White', color=[1, 1, 1, 1], font_size=26, bold=True))
        self.clb = Label(color=[1, 1, 1, 1], font_size=28, bold=True, text='2')
        self.clw = Label(color=[1, 1, 1, 1], font_size=28, bold=True, text='2')
        self.add_widget(self.clb)
        self.add_widget(self.clw)
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.canvas.before.clear()
        self.canvas.before.add(Color(rgb=[0.281, 0.363, 0.246]))
        self.canvas.before.add(Rectangle(pos=self.pos, size=self.size))
        self.canvas.after.clear()
        self.canvas.after.add(Color(rgb=[0, 0, 0]))
        self.canvas.after.add(Line(rectangle=[self.x, self.y, self.width, self.height], width=3))
        self.canvas.after.add(Line(points=[self.width/2 + self.x, self.y,
                                           self.width/2 + self.x, self.height + self.y], width=3))
        self.canvas.after.add(Line(points=[self.x, self.height/3 + self.y,
                                           self.width + self.x, self.height/3 + self.y], width=3))
        self.canvas.after.add(Line(points=[self.x, self.height/3 * 2 + self.y,
                                           self.width + self.x, self.height/3 * 2 + self.y], width=3))
    pass

class FieldWidget(Widget):
    def __init__(self, **kwargs):
        super(FieldWidget, self).__init__(**kwargs)
        # othelllo : 16.[48, 5D, 3F] / 10.[72, 93, 63] / %.[0.281, 0.363, 0.246]
        self.size = [800, 800]
        self.size_hint = [None, None]
        self.bind(pos=self.update)
        self.update()
    def update(self, *args):
        self.canvas.clear()
        self.canvas.add(Color(rgb=[0.281, 0.363, 0.246]))
        self.canvas.add(Rectangle(pos=self.pos, size=self.size))
        self.canvas.add(Color(rgb=[0, 0, 0]))
        self.canvas.add(Line(rectangle=[self.x, self.y, self.width, self.height], width=5))
        for i in range(1, 8):
            row = (self.height / 8 * i) + self.y
            rowLine = Line(points=[self.x, row, self.width + self.x, row],
                           width=3, cap='none', joint='none', close=False)
            self.canvas.add(rowLine)
        for i in range(1, 8):
            col = (self.width / 8 * i) + self.x
            colLine = Line(points=[col, self.y, col, self.height + self.y],
                           width=3, cap='none', joint='none', close=False)
            self.canvas.add(colLine)
        self.drawfield()
    def drawfield(self):
        poscalc = lambda z, wh: (wh / 16) + (wh / 8) * z
        rad = self.width / 8 * 0.4
        for i in range(8):
            ypos = (self.height - poscalc(i, self.height)) + self.y
            for j in range(8):
                xpos = poscalc(j, self.width) + self.x
                num = othello_alpha.field[(i, j)]
                if(num == 0):
                    pass
                elif(num == 1):
                    self.canvas.add(Color(rgb=[0, 0, 0]))
                    self.canvas.add(Ellipse(pos=[xpos-rad, ypos-rad], size=[rad*2, rad*2]))
                elif(num == 2):
                    self.canvas.add(Color(rgb=[0.9, 0.9, 0.9]))
                    self.canvas.add(Ellipse(pos=[xpos-rad, ypos-rad], size=[rad*2, rad*2]))
                    pass
                else:
                    print("FieldWidget drawfield Error")
                    sys.exit()
    def on_touch_down(self, touch):
        xpos = (touch.x - self.x) / (self.width / 8)
        ypos = 8 - (touch.y - self.y) / (self.height / 8)
        if(othello_alpha.Turn == othello_alpha.playerStone):
            if(len(player.getPossibleLocation()) == 0):
                othello_alpha.Turn = othello_alpha.computerStone
                pass
            else:
                if(0 <= int(xpos) and int(xpos) < 8 and 0 <= int(ypos) and int(ypos) < 8):
                    mypos = (int(ypos), int(xpos))
                    if(player.confPos(mypos)):
                        player.updateField(mypos)
                        othello_alpha.Turn = othello_alpha.computerStone
                        self.drawfield()
            pass
        elif(othello_alpha.Turn == othello_alpha.computerStone):
            mypos = comp.electRandom()
            if(mypos == None):
                othello_alpha.Turn = othello_alpha.playerStone
            else:
                comp.updateField(mypos)
                othello_alpha.Turn = othello_alpha.playerStone
                self.drawfield()
            pass
    pass


class PlayWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(PlayWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        # 左側
        anchor1 = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_x=2)
        anchor1.add_widget(FieldWidget())
        # 右側
        box = BoxLayout(orientation='vertical')
        anchor2 = AnchorLayout(anchor_x='center', anchor_y='center')
        self.cw = CountWidget()
        anchor2.add_widget(self.cw)
        self.tl = TurnLabel()
        anchor3 = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor3.add_widget(BtnReturn())
        box.add_widget(anchor2)
        box.add_widget(self.tl)
        box.add_widget(anchor3)
        # PlayWidget自身
        self.add_widget(anchor1)
        self.add_widget(box)
    pass

class BtnBlack(Button):
    def __init__(self, **kwargs):
        super(BtnBlack, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 1]
        self.background_normal = ''
        self.color = [1, 1, 1, 1]
        self.font_size = 36
        self.pos_hint = {'center_x':0.35, 'center_y':0.35}
        self.size_hint = [None, None]
        self.size = [200, 100]
        self.text = 'Black'
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.canvas.before.clear()
        self.canvas.before.add(Color(rgb=[0, 0, 0]))
        self.canvas.before.add(Line(rectangle=[self.x, self.y, self.width, self.height], width=3))
    def on_press(self):
        self.setStone()
        app = App.get_running_app()
        app.root.gotoPlayDisplay('Turn : You')
    def setStone(self):
        othello_alpha.playerStone = 1
        othello_alpha.computerStone = 2
        othello_alpha.Turn = othello_alpha.playerStone
        global player
        global comp
        player = Player(othello_alpha.playerStone, othello_alpha.computerStone)
        comp = Computer(othello_alpha.computerStone, othello_alpha.playerStone)
    pass

class BtnWhite(Button):
    def __init__(self, **kwargs):
        super(BtnWhite, self).__init__(**kwargs)
        self.background_color = [1, 1, 1, 1]
        self.background_normal = ''
        self.color = [0, 0, 0, 1]
        self.font_size = 36
        self.pos_hint = {'center_x':0.65, 'center_y':0.35}
        self.size_hint = [None, None]
        self.size = [200, 100]
        self.text = 'White'
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.canvas.before.clear()
        self.canvas.before.add(Color(rgb=[0, 0, 0]))
        self.canvas.before.add(Line(rectangle=[self.x, self.y, self.width, self.height], width=3))
    def on_press(self):
        self.setStone()
        app = App.get_running_app()
        app.root.gotoPlayDisplay('Turn : Computer')
    def setStone(self):
        othello_alpha.playerStone = 2
        othello_alpha.computerStone = 1
        othello_alpha.Turn = othello_alpha.computerStone
        global player
        global comp
        player = Player(othello_alpha.playerStone, othello_alpha.computerStone)
        comp = Computer(othello_alpha.computerStone, othello_alpha.playerStone)
    pass

class SelectTurn(FloatLayout):
    def __init__(self, **kwargs):
        super(SelectTurn, self).__init__(**kwargs)
        lb = Label(text='Select Turn Black(First) or White(Second).', color=[0, 0, 0, 1], font_size=48)
        lb.pos_hint = {'center_x':0.5, 'center_y':0.7}
        btnBlack = BtnBlack()
        btnWhite = BtnWhite()
        self.add_widget(lb)
        self.add_widget(btnBlack)
        self.add_widget(btnWhite)
    pass

class BtnStart(Button):
    def __init__(self, **kwargs):
        super(BtnStart, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 1]
        self.background_normal = ''
        self.font_size = 36
        self.pos_hint = {'center_x':0.5, 'center_y':0.3}
        self.size_hint = [None, None]
        self.size = [160, 100]
        self.text = 'Start'
    def on_press(self):
        #print('BtnStart')
        app = App.get_running_app()
        app.root.gotoSelectTurn()
    pass

class TitleWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(TitleWidget, self).__init__(**kwargs)
        # タイトル用のラベルとスタートボタンをTitleWidgetに追加
        self.add_widget(Label(text='Othello64', color=[0, 0, 0, 1], font_size=48, pos_hint={'center_x':0.5, 'center_y':0.7}))
        self.add_widget(BtnStart())
    pass


class RootWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.canvas.before.clear()
        self.canvas.before.add(Color(rgb=[1, 1, 1]))
        self.canvas.before.add(Rectangle(pos=self.pos, size=self.size))
    def gotoTitle(self):
        self.clear_widgets()
        self.add_widget(TitleWidget())
    def gotoSelectTurn(self):
        self.clear_widgets()
        self.add_widget(SelectTurn())
    def gotoPlayDisplay(self, turnText):
        self.clear_widgets()
        pw = PlayWidget()
        pw.tl.text = turnText
        self.add_widget(pw)
    pass

class OthelloApp(App):
    def build(self):
        root = RootWidget()
        root.gotoTitle()
        return root


if __name__ == '__main__':
    OthelloApp().run()
