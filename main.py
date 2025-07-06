import time
from autoclicker import AutoClicker
from gui import App
from multiprocessing import Process, Queue

if __name__ == '__main__':
    q = Queue()

    # Create the classes
    autoclicker = AutoClicker(q)
    gui = App(q)

    # Create the processes
    p2 = Process(target=autoclicker.check_for_stop)



# crashes when I click on Activate