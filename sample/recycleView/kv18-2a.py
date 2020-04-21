from random import sample
from string import ascii_lowercase

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

import japanize_kivy

class Test(BoxLayout):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)

        self.rv.data = []
        btn_list = ['ひつまぶし','味噌煮込みうどん','味噌カツ','台湾ラーメン' \
                    ,'手羽先','小倉トースト','きしめん','あんかけスパ','どて煮' \
                    ,'ういろう','甘口バナナスパ']
        for btn_list_any in btn_list:
            self.rv.data.append({'value': btn_list_any})


# ボタンクラス
class VariousButtons(BoxLayout):
    # ボタン押下処理
    def on_select_button(self, button):
        print('press:'+button.text)


class TestApp(App):
    def build(self):
        return Test()


if __name__ == '__main__':
    TestApp().run()