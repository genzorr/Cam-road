#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from watcher import *
from ui import MainWindow

class Control:
    def __init__(self):
        self._mode = 0
        self.left = 0
        self.right = 0
        self.set_base = 0

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value == 1:
            self.left = 0
            self.right = 0
        self._mode = value


#   TODO: think about advantages of properties (I should add there smth else)
#   TODO: all processing should be on the road
#   TODO: change velocity QSlider to QProgressBar

if __name__ == "__main__":
    app = QApplication(sys.argv)

    control = Control()
    window = MainWindow(control=control)
    window.show()

    thread = WatcherThread(window=window, control=control)
    thread.start()

    sys.exit(app.exec_())
