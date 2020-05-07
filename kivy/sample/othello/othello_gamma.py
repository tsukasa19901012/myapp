# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.lang import Builder

import sys
sys.dont_write_bytecode = True

import numpy as np

import othello_alpha
from othello_alpha import Player, Computer, setField

Builder.load_file('othello_gamma.kv')

class FieldWidget(Widget):
    def drawField(self):
        self.canvas.clear()
        self.canvas.add(Color(rgb=[0.281, 0.363, 0.246]))
        self.canvas.add(Rectangle(pos=self.pos, size=self.size))
        self.canvas.add(Color(rgb=[0, 0, 0]))
        self.canvas.add(Line(rectangle=[self.x, self.y, self.width, self.height], width=5))
        self.drawRowLine()
        self.drawColLine()
        self.drawStone()
        pass
    def drawRowLine(self):
        for i in range(1, 8):
            row = (self.height / 8 * i) + self.y
            rowLine = Line(width=3)
            rowLine.points = [self.x, row, self.width + self.x, row]
            self.canvas.add(rowLine)
            pass
    def drawColLine(self):
        for i in range(1, 8):
            col = (self.width / 8 * i) + self.x
            colLine = Line(width=3)
            colLine.points = [col, self.y, col, self.height + self.y]
            self.canvas.add(colLine)
            pass
    def drawStone(self):
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
                    self.canvas.add(Color(rgb=[1, 1, 1]))
                    self.canvas.add(Ellipse(pos=[xpos-rad, ypos-rad], size=[rad*2, rad*2]))
                    pass
                else:
                    print("FieldWidget drawField Error")
                    sys.exit()
    def on_touch_down(self, touch):
        xpos = int((touch.x - self.x) / (self.width / 8))
        ypos = int(8 - (touch.y - self.y) / (self.height / 8))
        if(othello_alpha.Turn == othello_alpha.playerStone):
            mypos = (ypos, xpos)
            if(len(player.getPossibleLocation()) == 0):
                othello_alpha.Turn = othello_alpha.computerStone
                self.parent.parent.ids.TurnLabel.text = 'Turn : Computer'
            else:
                if(player.confPos(mypos)):
                    player.updateField(mypos)
                    self.drawField()
                    othello_alpha.Turn = othello_alpha.computerStone
                    self.parent.parent.ids.TurnLabel.text = 'Turn : Computer'
            pass
        elif(othello_alpha.Turn == othello_alpha.computerStone):
            mypos = comp.electRandom()
            if(mypos != None):
                comp.updateField(mypos)
                self.drawField()
            othello_alpha.Turn = othello_alpha.playerStone
            self.parent.parent.ids.TurnLabel.text = 'Turn : You'
        else:
            pass
        self.parent.parent.ids.clb.text = str(len(list(zip(*np.where(othello_alpha.field == 1)))))
        self.parent.parent.ids.clw.text = str(len(list(zip(*np.where(othello_alpha.field == 2)))))
        if(len(player.getPossibleLocation()) == 0 and len(comp.getPossibleLocation()) == 0):
            self.parent.parent.ids.TurnLabel.text = othello_alpha.confResult()
    pass

class SelectTurn(FloatLayout):
    def setStoneBlack(self):
        othello_alpha.playerStone = 1
        othello_alpha.computerStone = 2
        othello_alpha.Turn = othello_alpha.playerStone
    def setStoneWhite(self):
        othello_alpha.playerStone = 2
        othello_alpha.computerStone = 1
        othello_alpha.Turn = othello_alpha.computerStone
    pass

class RootWidget(FloatLayout):
    def gotoTitle(self):
        self.clear_widgets()
        self.add_widget(Factory.TitleWidget())
    def gotoSelectTurn(self):
        self.clear_widgets()
        self.add_widget(Factory.SelectTurn())
    def gotoPlayDisplay(self):
        pw = Factory.PlayWidget()
        pw.ids.clb.text = '2'
        pw.ids.clw.text = '2'
        pw.ids.BlackTurn.text = 'You' if(othello_alpha.playerStone == 1) else 'Computer'
        pw.ids.WhiteTurn.text = 'You' if(othello_alpha.playerStone == 2) else 'Computer'
        pw.ids.TurnLabel.text = 'Turn : ' + pw.ids.BlackTurn.text
        global player
        global comp
        player = Player(othello_alpha.playerStone, othello_alpha.computerStone)
        comp = Computer(othello_alpha.computerStone, othello_alpha.playerStone)
        self.clear_widgets()
        self.add_widget(pw)
    def setField(self):
        othello_alpha.field = setField()
    pass

class OthelloApp(App):
    def build(self):
        root = RootWidget()
        root.gotoTitle()
        return root

if __name__ == '__main__':
    OthelloApp().run()
