# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

class SwitchButton(Button):
    def on_press(self):
        if 'START' == self.text:
            self.text = 'END'
        else:
            self.text = 'START'

class MyRoot(FloatLayout):
    pass

class TittleApp(App):
    pass

TittleApp().run()
