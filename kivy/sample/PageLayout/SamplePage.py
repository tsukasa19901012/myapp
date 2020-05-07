# -*- coding: utf-8 -*-
import glob
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle

from kivy.lang import Builder
Builder.load_file('SamplePage.kv')

class TestWidget(PageLayout):
    pass


# ======== アプリケーション　===========
# アプリケーションの説明
# 同じフォルダにある「img」フォルダの画像を
# 順番にページにするアプリケーションです。
class MyImage(AnchorLayout):
    def __init__(self, src, **kwargs):
        super(MyImage, self).__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        self.add_widget(Image(source=src))
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()
    def update(self, *args):
        self.canvas.before.clear()
        self.canvas.before.add(Color(rgb=[1, 1, 1]))
        self.canvas.before.add(Rectangle(pos=self.pos, size=self.size))
    pass

class RootWidget(PageLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        # files = glob.glob('./img/*')
        # sampleディレクトリをworkspaceにしている場合は以下を使用
        files = glob.glob('./sample/PageLayout/img/*')
        for file in files:
            self.add_widget(MyImage(file))
    pass

class SamplePageLayoutApp(App):
    def build(self):
        root = RootWidget()
        return root

if __name__ == '__main__':
    SamplePageLayoutApp().run()
