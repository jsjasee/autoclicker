from pynput import keyboard
import pynput.mouse
from tkinter import *
from tkinter import messagebox
import pyautogui
from multiprocessing import Process, Queue
import time

DISALLOWED_KEYS = [
    "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
    "Caps_Lock", "Num_Lock", "Scroll_Lock", "Meta_L", "Insert", "Pause",
    "Print", "Escape", "BackSpace", "Tab", "Return", "space",
    "Up", "Down", "Left", "Right",
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "Home", "End", "Prior", "Next",  # PageUp/PgDn
]

def keyboard_listener(g_queue, l_queue):

    previous_key = ['None']
    stop_key = ['p']
    start_key = ['q']

    def check_queue():
        if not l_queue.empty():
            messages = l_queue.get()
            print(messages)
            start_key[0] = messages['start_key']
            stop_key[0] = messages['stop_key']

    def on_press(key):
        try:
            if key.char == stop_key[0]:
                g_queue.put('end')
                previous_key[0] = stop_key[0]
                print('detected stop signal')
                # return False # just don't return anything and the keyboard listener will not stop!
            elif key.char == start_key[0]:
                if previous_key[0] == stop_key[0]:
                    # to avoid users from spamming 'q' which will make the autoclicker go faster since it keeps triggering the queue
                    # todo: but if i want to implement unhinged mode have to turn this off, which means i have to keep the default start and stop keys?
                    # todo: also investigate how to pass the keys that users entered to keyboard listener, might want to save first.
                    g_queue.put('start')
                    previous_key[0] = start_key[0]
                    print('detected start signal')
                # return True
        except AttributeError:
            # Will ignore special keys pressed
            pass

    # start a listener thread
    listener = keyboard.Listener(on_press=on_press)  # do i need to supply the argument 'key' inside when passing in the function as an input or no need cos automatically supplied by pynput
    listener.start()
    # listener.join() is needed only if nothing else in the function keeps the process alive. When you call listener.start(), it runs in a separate background thread — but if your main function finishes running (i.e. doesn't loop, wait, or block), then Python will exit the process entirely.
    # So the listener doesn't stop on its own — Python just kills the process because there's nothing left running in the main thread.
    # listener.join()
    while True:
        time.sleep(0.01)
        check_queue()
        # this keeps the process alive since there is something for the function to do,
        # now we can implement the check_queue function to check for any messages sent over from tkinter AND also run our listener at the same time

def run_gui(g_queue, l_queue): # g for GUI, l for listener

    # Because nested functions cannot modify variables in outer scopes unless they’re mutable (like a list).

    # todo: add a tickbox for unhinged mode - basically can keep clicking 'q' to speed up the autoclicker, just don't remove the previous click job lol -> aka just dont even set the click_job to None, just let it run
    # but this might be unsafe since it might overload the computer -> so best to stick to 0.01s, seems like the fastest already
    should_click = [False]
    click_job = ['None']

    def run_autoclicker():
        # check click interval
        try:
            new_cooldown = float(click_interval.get())
        except ValueError:
            response = messagebox.showwarning(title='INVALID CLICK INTERVAL', message=f'Please make sure ONLY NUMBERS are entered. Do NOT enter strings. A default value of {cooldown[0]}s is used instead.')
        else:
            if new_cooldown < 0.01:
                response = messagebox.showwarning(title='CLICK INTERVAL TOO SHORT', message=f'Click interval is too short, a default value of {cooldown[0]}s is used instead.')
            else:
                cooldown[0] = new_cooldown
                response = messagebox.showinfo(title='Successfully configured!', message='Press ok to start the autoclicker!')

        # todo: check the start and end keys are the same, if yes reject. also check if start and end keys are keys on the keyboard, currently support alphabets, numbers and special keys like esc, tab, tilda
        start_key = start_key_button.cget('text')
        end_key = disabling_key_button.cget('text')
        typed_key = key_button.cget('text')
        if start_key == end_key or start_key == typed_key or end_key == typed_key or start_key in DISALLOWED_KEYS or end_key in DISALLOWED_KEYS or typed_key in DISALLOWED_KEYS:
            response_for_keys = messagebox.showwarning(title='INVALID KEYS', message='Overlapping start,end or typed keys OR unsupported keys detected. Default keys for start: q, and end: p, are used instead.')
            start_key_button.config(text='q')
            disabling_key_button.config(text='p')
            key_button.config(text='No key is selected')
        else:
            print(start_key_button.cget('text'))
            print(disabling_key_button.cget('text'))
            keys_message = {'type': 'start_end_keys',
                            'start_key': start_key_button.cget('text'),
                            'stop_key': disabling_key_button.cget('text'),}
            l_queue.put(keys_message)
            response_for_keys = messagebox.showinfo(title='Success!', message='Successfully configured keys!')

        if response and response_for_keys:
            description.config(text='Clicking!')
            g_queue.put('start') # activates the clicker!

    def start_listening(target_button):
        def when_pressed(event):
            print(f"You pressed {event.keysym}") # event.keysym shows the name of the keys typed
            target_button.config(text=event.keysym)
            window.unbind("<Key>") # when the key is printed then unbind again so that each button click only tracks ONE KEY

        window.bind("<Key>", when_pressed)

    def click():
        print('its clicking!')
        print(click_interval.cget('text'))
        start_time = time.time()
        if should_click[0]:
            # pyautogui.click()
            # Avoid using pyautogui.click() for very fast clicking.
            # pyautogui.click() is designed for human-like consistency, and each click takes ~50–100ms.
            # To achieve faster, lower-latency clicking (e.g., gaming-level speed), use pynput.mouse instead:
            mouse.press(pynput.mouse.Button.left)
            mouse.release(pynput.mouse.Button.left)
            if key_button.cget('text') != start_key_button.cget('text') and key_button.cget('text') != disabling_key_button.cget('text'):
                pyautogui.press(key_button.cget('text'))  # c in cget means configuration get, means get the configuration options of the button, like its text
                # exclude the stop keys and start keys
            print(int(cooldown[0] * 1000))
            stop_time = time.time()
            print(f'Click took {stop_time - start_time} seconds')
            click_job[0] = window.after(int(cooldown[0] * 1000), click) # change it to 10 instead of using variable

    def check_queue():
        if not g_queue.empty(): # this is not a while True: loop, so tkinter mainloop remains free to run in the background
            message = g_queue.get()
            if message == 'start':
                should_click[0] = True
                if click_job[0]:
                    # if there are existing click_jobs, cancel them. eg. if you press activate, then press Q again, this will create 2 click loops that keeps running at the same time, making the clicks appear faster.
                    window.after_cancel(click_job[0])
                description.config(text='Clicking! (start with hotkey)')
                click()
            elif message == 'end':
                should_click[0] = False
                click_job[0] = 'None'
                description.config(text='STOPPED! (stop with hotkey)')
                print('stopped clicking')

        window.after(int(cooldown[0] * 1000), check_queue) # why need this line if there's already a window.after in the run() function...?
        # window.after() ONLY CALLS IT ONCE AFTER THAT SET DURATION, TO MAKE IT REPEAT (while loop) YOU NEED TO HAVE WINDOW.AFTER AGAIN IN THE SAME FUNCTION.

    def run():
        window.after(int(cooldown[0] * 1000), check_queue) # after 5s it will start the while loop to check_queue
        window.mainloop()

    window = Tk()
    window.title("Autoclicker")

    # Create mouse
    mouse = pynput.mouse.Controller()

    # Add title
    title = Label(text="Pytoclicker", font=("Helvetica", 30, "bold"))
    description = Label(text="Click on the buttons to map keys.")
    title.grid(column=0, row=0, columnspan=2)
    description.grid(column=0, row=1, columnspan=2)

    # Add click_interval entry
    click_interval_label = Label(text="Click Interval: ")
    click_interval_label.grid(column=0, row=2)
    click_interval = Entry()
    click_interval.grid(column=1, row=2)

    # Add the key
    key_label = Label(text="Key to press: ")
    key_label.grid(column=0, row=3)
    key_button = Button(text="No key selected.", command=lambda: start_listening(key_button))
    key_button.grid(column=1, row=3)

    # Add the start key
    start_key_label = Label(text="Start key: ")
    start_key_label.grid(column=0, row=4)
    start_key_button = Button(text="q", command=lambda: start_listening(start_key_button))
    start_key_button.grid(column=1, row=4)

    # Add the disabling key
    disabling_key_label = Label(text="Disabling key: ")
    disabling_key_label.grid(column=0, row=5)
    disabling_key_button = Button(text="p", command=lambda: start_listening(disabling_key_button))
    disabling_key_button.grid(column=1, row=5)

    # Activate button
    activate_button = Button(text="ACTIVATE!", command=run_autoclicker)
    activate_button.grid(column=0, row=6, columnspan=2)

    # Clicking status
    cooldown = [0.01]

    run()

if __name__ == "__main__":

    gui_queue = Queue()
    listener_queue = Queue()
    # we need 2 queues because right now, keyboard_listener just sends stuff to the gui, and gui just takes messages from the queue.
    # however, now keyboard_listener also needs to receive messages from the gui program.
    # if use only 1 queue, the moment we use queue.get() in the keyboard_listener function, it will also take away the 'start' message from the queue, and auto-clicker will not click.
    # hence need 2 separate queues to resolve the issue

    p1 = Process(target=keyboard_listener, args=(gui_queue,listener_queue))
    p2 = Process(target=run_gui, args=(gui_queue,listener_queue))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

# ========================
# Understanding Multiprocessing Join
# ========================

# The main Python script is the *parent process*.
# When we use multiprocessing.Process(target=...), we create *child processes*.
# The function passed to the process is NOT the child itself — it's the code that runs *within* the child process.

# .start() begins execution of the child process in parallel.
# .join() tells the *main process* to WAIT until the specific child process finishes.
# If we do not .join(), the main program may exit early and kill any child processes still running.

# This is especially important when child processes write to files or share data — without .join(),
# you might run into incomplete file writes, 'file not found' errors, or data corruption.

# It's not necessary to call .join() on *every* process, but we should join those that:
# - Must finish before the program ends
# - Interact with shared resources like files, databases, or queues

# Note: main.py is the file we are running, and our code runs in the main thread by default, the main thread starts running at -> if __name__ == '__main__':
# Important: calling p1.join() will block the main thread until p1 is done,
# but since p1 and p2 were both started already (via .start()), they run *in parallel*.
# So calling p1.join() does NOT prevent p2 from running at the same time.

# This ensures our autoclicker and keyboard listener both complete cleanly.




