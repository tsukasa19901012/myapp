# -*- coding: utf-8 -*-
import japanize_kivy
import sys
sys.dont_write_bytecode = True

from kivy.app import App
from kivy.core.window import Window
Window.size = (480, 720)

from kivy.factory import Factory

import types
from kivy.clock import Clock

def start_coro(coro):
    def step_coro(*args, **kwargs):
        try:
            coro.send((args, kwargs, ))(step_coro)
        except StopIteration:
            pass
    try:
        coro.send(None)(step_coro)
    except StopIteration:
        pass


async def thread(func, *args, **kwargs):
    from threading import Thread
    return_value = None
    is_finished = False
    def wrapper(*args, **kwargs):
        nonlocal return_value, is_finished
        return_value = func(*args, **kwargs)
        is_finished = True
    Thread(target=wrapper, args=args, kwargs=kwargs).start()
    while not is_finished:
        await sleep(3)
    return return_value


@types.coroutine
def sleep(duration):
    args, kwargs = yield lambda step_coro: Clock.schedule_once(step_coro, duration)
    return args[0]


@types.coroutine
def event(ed, name):
    bind_id = None
    step_coro = None
    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = ed.fbind(name, callback)
        assert bind_id > 0  # bindingに成功したか確認
        step_coro = step_coro_
    def callback(*args, **kwargs):
        ed.unbind_uid(name, bind_id)
        step_coro(*args, **kwargs)
    return (yield bind)

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
        start_coro(self.some_task())

    async def some_task(self):
        self.view = ModalWindow()
        self.view.ids.label.text = '1つめ'
        print('1つめモーダル画面表示呼び出し START')
        self.view.open()
        print('1つめview.value = ', self.view.value) # view.value =  0
        await event(self.view, 'on_dismiss')  # modalが閉じられるまで待つ
        print('1つめview.value = ', self.view.value)# view.value =  1
        print('1つめモーダル画面表示呼び出し END')
        print('view再定義')
        await sleep(3)
        await self.function2('2') # 2番目
        self.function1('3') # 6番目
        self.function1('4') # 5番目
        await self.function2('5') # 3番目
        await self.function3('6') # 4番目

    def function1(self, num):
        start_coro(self.function2(num))

    async def function2(self, num):
        self.view = ModalWindow()
        self.view.ids.label.text = num + 'つめ'
        print(num + 'つめモーダル画面表示呼び出し START')
        self.view.open()
        print(num + 'つめview.value = ', self.view.value) # view.value =  0
        await event(self.view, 'on_dismiss')  # modalが閉じられるまで待つ
        print(num + 'つめview.value = ', self.view.value)# view.value =  1
        print(num + 'つめモーダル画面表示呼び出し END')

    async def function3(self, num):
        await self.function2(num)

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
