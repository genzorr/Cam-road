#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from ui import MainWindow, QWorkWidget
from watcher import *

#   TODO: think about advantages of properties (I should add there smth else)
#   TODO: all processing should be on the road
#   TODO: change velocity QSlider to QProgressBar

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    thread = WatcherThread(window=window)
    thread.start()

    sys.exit(app.exec_())
