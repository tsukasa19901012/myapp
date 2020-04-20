# -*- coding: utf-8 -*-
import japanize_kivy
import sys
sys.dont_write_bytecode = True

from kivy.app import App
from rootWidget import RootWidget

class ScreenTransitionApp(App):
    def build(self):
        self.title = 'XENO'
        root = RootWidget()
        root.gotoTitle()
        return root

if __name__ == '__main__':
    ScreenTransitionApp().run()
