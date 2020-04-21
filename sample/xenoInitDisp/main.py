# -*- coding: utf-8 -*-
import japanize_kivy
import sys
sys.dont_write_bytecode = True

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout

class XenoRootWidget(FloatLayout):
    def gotoInit(self):
        self.clear_widgets()
        self.add_widget(Factory.XenoMainWidget())
    pass

class XenoApp(App):
    def build(self):
        self.title = 'XENO'
        root = XenoRootWidget()
        root.gotoInit()
        return root

if __name__ == '__main__':
    XenoApp().run()
