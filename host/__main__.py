#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from watcher import *
from ui import MainWindow

class Control:
    def __init__(self):
        self.mode = 0
        self.direction = 0
        self.set_base = 0


#   TODO: think about advantages of properties (I should add there smth else)

#   TODO: CONNECT BUTTONS TO DATA CLASSES
#   TODO: ADD LOCK TO THREADS

#   TODO: USE ISINSTANSE

if __name__ == "__main__":
    app = QApplication(sys.argv)

    control = Control()
    window = MainWindow(control=control)
    window.show()

    # mbee_thread = MbeeThread()

    thread = WatcherThread(window=window, control=control)
    thread.start()

    sys.exit(app.exec_())

