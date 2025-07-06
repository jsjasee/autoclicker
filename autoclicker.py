import time
import threading
from threading import Thread

import pyautogui
from pynput import keyboard

class AutoClicker:
    def __init__(self, queue):
        self.queue = queue
        self.cooldown = 0.01
        self.should_stop = False
        self.stop_key = 'p'
        self.start_key = 'q'

    def start_click_thread(self, button_to_press):
        clicker_thread = Thread(target=self.click, args=(button_to_press,), daemon=True) # args must be a tuple
        clicker_thread.start()

    def click(self, button_to_press):
        while True:
            if not self.should_stop:
                print('its clicking!')
                pyautogui.click()
                pyautogui.press(button_to_press)
                time.sleep(self.cooldown)
            else:
                time.sleep(1)

    def check_for_stop(self):

        def on_press(key):
            try:
                if key.char == self.stop_key:
                    self.should_stop = True
                    self.queue.put('end')
                    # return False # just don't return anything and the keyboard listener will not stop!
                elif key.char == self.start_key:
                    self.should_stop = False
                    self.queue.put('start')
                    # return True
            except AttributeError:
                pass

        # start a listener thread
        listener = keyboard.Listener(on_press=on_press) # do i need to supply the argument 'key' inside when passing in the function as an input or no need cos automatically supplied by pynput
        listener.start()

        # while True: -> this is VERY BAD. creates a new listener every time the loop runs
        #     with keyboard.Listener(on_press=on_press) as listener:
        #         # listener.start() -> there is no need to write this line because 'with as' already call listener.start() for you!
        #         if not self.should_stop:
        #             self.click()