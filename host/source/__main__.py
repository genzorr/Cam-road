#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import os.path as path
import signal
import sys
import time

import hjson
from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication

import global_
from mbee_ import MBeeThread
from ui.ui import MainWindow
from watcher import WatcherThread, ControlThread
from lib.data_classes import HTRData, HBData, RTHData

os.environ['DISPLAY'] = ':0'

THREADS = []

# Killer provides a soft way to kill your application.
class Killer:
    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, self.kill)

    def kill(self):
        for thread in THREADS:
            thread.alive = False
            thread.off()

        print('exiting..')
        time.sleep(1)
        sys.exit()

# Gets absolute path to ../../
def get_dir_path():
    filepath = path.abspath(__file__)
    dirname = path.dirname(filepath)
    dirname_parent = path.split(dirname)[0]
    return path.split(dirname_parent)[0]


if __name__ == "__main__":
    # Set up Killer to enable soft exiting by button in app.
    global_.killer = Killer()
    app = QApplication(sys.argv)

    # Config file data.
    f = open(get_dir_path() + '/config.json')
    config = hjson.loads(f.read())
    global_.TX_ADDR_HOST = config["TX_ADDR_HOST"]
    global_.TX_ADDR_ROAD = config["TX_ADDR_ROAD"]
    global_.settings = config

    # Set up mutex.
    global_.mutex = QMutex()
    global_.flag = True

    # Create global data classes.
    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    # Create main window.
    global_.window = MainWindow()
    global_.window.show()

    # Set up threads.
    global_.mbeeThread = MBeeThread()
    global_.mbeeThread.start()
    THREADS.append(global_.mbeeThread)

    global_.watcher = WatcherThread()
    global_.watcher.start()
    THREADS.append(global_.watcher)

    global_.controlThread = ControlThread()
    global_.controlThread.start()
    THREADS.append(global_.controlThread)

    sys.exit(app.exec_())

