#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, signal, os, subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex

from watcher import *
from mbee_ import *
from ui.ui import MainWindow

os.environ['DISPLAY'] = ':0'
#   TODO: think about advantages of properties (I should add there smth else)

#   TODO: CONNECT BUTTONS TO DATA CLASSES
#   TODO: make indication when normal / error exiting
#   TODO: ADD LOCK TO THREADS!!!!!!!!!!!!!!!!!!!!!
#   FIXME: CRC
#
#   BUGS: in buttons switches, when lock button is pushed

# ssh -X pi@10.0.0.10 x2x -west -to :0
# sudo stty -F /dev/ttySAC3 19200 cs8 -cstopb -parenb cread time 1 min 0
# sudo ~/Downloads/modbus-cli/src/modbus -r -d /dev/ttySAC3 -b 115200 -f 3 -s 2 -a 0 -n 20

# radio UP
# echo 63 > /sys/class/gpio/export
# echo out > /sys/class/gpio/gpio63/direction
# echo 1 > /sys/class/gpio/gpio63/value
# echo 63 > /sys/class/gpio/unexport

THREADS = []

class Killer:
    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, self.kill)

    def kill(self):
        for thread in THREADS:
            thread.alive = False
            thread.off()
        subprocess.call('./radio_off.sh')
        print('radio off')

        print('exiting..')
        time.sleep(1)
        sys.exit()


if __name__ == "__main__":
    global_.killer = Killer()
    app = QApplication(sys.argv)

    global_.mutex = QMutex()

    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    window = MainWindow()
    window.show()

    global_.mbeeThread = MbeeThread()
    global_.mbeeThread.start()
    THREADS.append(global_.mbeeThread)

    global_.watcher = WatcherThread(window=window)
    global_.watcher.start()
    THREADS.append(global_.watcher)

    global_.controlThread = ControlThread(window=window)
    global_.controlThread.start()
    THREADS.append(global_.controlThread)

    sys.exit(app.exec_())
