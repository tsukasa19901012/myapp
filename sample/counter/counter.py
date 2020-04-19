from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

Label.font_size = 32

class IncreaseButton(Button):
    def on_press(self):
        lbl = self.parent.parent.lbl
        lbl.value = lbl.value + 1
        lbl.text = str(lbl.value)

class ResetButton(Button):
    def on_press(self):
        lbl = self.parent.parent.lbl
        lbl.value = 0
        lbl.text = str(lbl.value)

class MyRoot(BoxLayout):
    orientation = 'horizontal'
    def __init__(self, **kwargs):
        super(MyRoot, self).__init__(**kwargs)
        self.lbl = Label(text='0')
        self.lbl.value = 0
        self.add_widget(self.lbl)
        box = BoxLayout(orientation='vertical')
        btn1 = IncreaseButton(text='Increase')
        btn2 = ResetButton(text='Reset')
        box.add_widget(btn1)
        box.add_widget(btn2)
        self.add_widget(box)

class counterApp(App):
    def build(self):
        return MyRoot()

counterApp().run()