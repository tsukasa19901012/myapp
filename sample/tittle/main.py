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


class TittleApp(App):
    def build(self):
        layout = FloatLayout()
        btn = SwitchButton()
        layout.add_widget(btn)
        return layout

TittleApp().run()
