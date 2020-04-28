# -*- coding: utf-8 -*-
import japanize_kivy
import sys
sys.dont_write_bytecode = True

from kivy.app import App
from kivy.core.window import Window
Window.size = (480, 720)

from kivy.factory import Factory

def start_generator(gen):
    def step_gen(*args, **kwargs):
        try:
            gen.send((args, kwargs, ))(step_gen)
        except StopIteration:
            pass

    try:
        gen.send(None)(step_gen)
    except StopIteration:
        pass

def event(ed, name):
    bind_id = None
    step_gen = None

    def bind(step_gen_):
        nonlocal bind_id, step_gen
        bind_id = ed.fbind(name, callback)
        assert bind_id > 0  # bindingに成功したか確認
        step_gen = step_gen_

    def callback(*args, **kwargs):
        ed.unbind_uid(name, bind_id)
        step_gen(*args, **kwargs)

    return bind

class ModalWindow(Factory.ModalView):
    value = Factory.StringProperty()
    def open(self, *args):
        print('モーダルが開かれました。')
        self.value = '0'
        super().open(self, *args)
    
    def dismiss(self, *args):
        print('モーダルが閉じられました。')
        self.value = '1'
        super().dismiss(self, *args)

class StartButton(Factory.Button):    
    def on_press(self):
        start_generator(self.some_task())

    def some_task(self):
        view = ModalWindow()
        print('モーダル画面表示呼び出し START')
        view.open()
        print('view.value = ', view.value)
        yield event(view, 'on_dismiss')  # modalが閉じられるまで待つ
        print('view.value = ', view.value)
        print('モーダル画面表示呼び出し END')

class MainRootWidget(Factory.FloatLayout):
    def gotoTitle(self):
        self.clear_widgets()
        print('初期タイトル画面表示呼び出し START')
        self.add_widget(Factory.TitleWidget())
        print('初期タイトル画面表示呼び出し END')
    pass

class MainApp(App):
    def build(self):
        self.title = 'yield'
        root = MainRootWidget()
        root.gotoTitle()
        return root

if __name__ == '__main__':
    MainApp().run()
