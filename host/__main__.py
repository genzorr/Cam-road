#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, signal, os
from PyQt5.QtWidgets import QApplication

from watcher import *
from ui import MainWindow

os.environ['DISPLAY'] = ':0'
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

    global_.mbee_thread_write = MbeeThread_write()
    global_.mbee_thread_write.start()

    global_.mbee_thread_read = MbeeThread_read()
    global_.mbee_thread_read.start()

    global_.watcher = WatcherThread(window=window)
    global_.watcher.start()
    sys.exit(app.exec_())

    # data = b'~\xa5\x00\x00@@\x00\x00@@\x00\x00pA\xfd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    # print(struct.unpack('f', data[10:14]))
