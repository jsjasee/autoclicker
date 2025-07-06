from threading import Thread
from tkinter import *
from autoclicker import AutoClicker

autoclicker = AutoClicker()

class App:
    def __init__(self, queue):
        self.queue = queue
        self.window = Tk()
        self.window.title("Autoclicker")

        # Add title
        self.title = Label(text="Pytoclicker", font=("Helvetica", 30, "bold"))
        self.description = Label(text="Click on the buttons to map keys.")
        self.title.grid(column=0, row=0, columnspan=2)
        self.description.grid(column=0, row=1, columnspan=2)

        # Add click_interval entry
        self.click_interval_label = Label(text="Click Interval: ")
        self.click_interval_label.grid(column=0, row=2)
        self.click_interval = Entry()
        self.click_interval.grid(column=1, row=2)

        # Add the key
        self.key_label = Label(text="Key to press: ")
        self.key_label.grid(column=0, row=3)
        self.key_button = Button(text="No key selected.", command=lambda: self.start_listening(self.key_button))
        self.key_button.grid(column=1, row=3)

        # Add the start key
        self.start_key_label = Label(text="Start key: ")
        self.start_key_label.grid(column=0, row=4)
        self.start_key_button = Button(text="q", command=lambda: self.start_listening(self.start_key_button))
        self.start_key_button.grid(column=1, row=4)

        # Add the disabling key
        self.disabling_key_label = Label(text="Disabling key: ")
        self.disabling_key_label.grid(column=0, row=5)
        self.disabling_key_button = Button(text="p", command=lambda: self.start_listening(self.disabling_key_button))
        self.disabling_key_button.grid(column=1, row=5)

        # Activate button
        self.activate_button = Button(text="ACTIVATE!", command=self.run_clicker_thread)
        self.activate_button.grid(column=0, row=6, columnspan=2)

        self.window.mainloop()

    def start_listening(self, target_button):

        def when_pressed(event):
            print(f"You pressed {event.keysym}") # event.keysym shows the name of the keys typed
            target_button.config(text=event.keysym)
            self.window.unbind("<Key>") # when the key is printed then unbind again so that each button click only tracks ONE KEY


        self.window.bind("<Key>", when_pressed)
        # this line is saying: Track whatever key (as determined by '<Key>') is being pressed, and then run the function, 'when_pressed',
        # when the Tkinter window, as determined by 'self.window' is focus and active

    def run_autoclicker(self):
        self.window.after(100, self.window.iconify) # iconify minimises the window
        # need to use threading cos we cannot have 2 while loops running at the same time. Tkinter window is another while loop cos it keeps the gui program active.
        # also need to solve the issue of that while True loop in the autoclicker.click() function. -> put this one in another thread.
        # that means now we have one thread listening for keyboard keys, another thread clicking, and the main thread keeping the main program alive

        autoclicker.start_click_thread(button_to_press=self.key_button.cget('text')) # c in cget means configuration get, means get the configuration options of the button, like its text

    def run_clicker_thread(self):
        thread = Thread(target=self.run_autoclicker, daemon=True)
        thread.start()

        # if got diff processes running then no need for threading typically