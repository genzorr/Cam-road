#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from ui import MainWindow
from watcher import *

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    baudrate = 9600
    port = '/dev/ttyUSB0'
    thread = WatcherThread(baudrate, port, window)
    thread.start()

    sys.exit(app.exec_())
