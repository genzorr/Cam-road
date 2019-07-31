#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from ui import MainWindow
from serial_tr import *

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # device = serial_init(9600)
    # while 1 and device:
    #     ans = serial_recv(device)
    #     if ans != "":
    #         print(ans)
    # window.workWidget.acceleration_signal.emit(0)

    thread = WatcherThread()
    thread.data_signal.connect(window.workWidget.ui.Acceleration.setValue)
    thread.data_signal.emit(0)

    thread.start()

    sys.exit(app.exec_())
