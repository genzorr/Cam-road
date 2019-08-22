#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, signal
from PyQt5.QtWidgets import QApplication

from watcher import *
from ui import MainWindow

#   TODO: think about advantages of properties (I should add there smth else)

#   TODO: CONNECT BUTTONS TO DATA CLASSES
#   TODO: make indication when normal/ error exiting
#   TODO: ADD LOCK TO THREADS!!!!!!!!!!!!!!!!!!!!!
#   FIXME: CRC

#   TODO: USE ISINSTANSE


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    window = MainWindow()
    window.show()

    global_.serial_device = serial_init()

    global_.mbee_thread = MbeeThread()
    global_.mbee_thread.start()

    global_.watcher = WatcherThread(window=window)
    global_.watcher.start()
    sys.exit(app.exec_())

    # data = b'~\xa5\x00\x00@@\x00\x00@@\x00\x00pA\xfd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    # print(struct.unpack('f', data[10:14]))
