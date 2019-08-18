#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from watcher import *
from ui import MainWindow

#   TODO: think about advantages of properties (I should add there smth else)

#   TODO: CONNECT BUTTONS TO DATA CLASSES
#   TODO: ADD LOCK TO THREADS

#   TODO: USE ISINSTANSE

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # mbee_thread = MbeeThread()

    thread = WatcherThread(window=window)
    thread.start()

    sys.exit(app.exec_())
    # data = b'~\xa5\x00\x00@@\x00\x00@@\x00\x00pA\xfd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    # print(struct.unpack('f', data[10:14]))

