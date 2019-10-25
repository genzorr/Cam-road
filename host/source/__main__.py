#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, signal, os
from PyQt5.QtWidgets import QApplication

from watcher import *
from ui.ui import MainWindow

os.environ['DISPLAY'] = ':0'
#   TODO: think about advantages of properties (I should add there smth else)

#   TODO: CONNECT BUTTONS TO DATA CLASSES
#   TODO: make indication when normal/ error exiting
#   TODO: ADD LOCK TO THREADS!!!!!!!!!!!!!!!!!!!!!
#   FIXME: CRC
#
#   BUGS: in buttons switches, when lock button is pushed

#   TODO: USE ISINSTANSE

# ssh -X pi@10.0.0.10 x2x -west -to :0
# sudo stty -F /dev/ttySAC3 19200 cs8 -cstopb -parenb cread time 1 min 0
# sudo ~/Downloads/modbus-cli/src/modbus -r -d /dev/ttySAC3 -b 115200 -f 3 -s 2 -a 0 -n 20
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    window = MainWindow()
    window.show()

    # global_.mbeeThread = MbeeThread()
    # global_.mbeeThread.start()

    global_.watcher = WatcherThread(window=window)
    global_.watcher.start()

    global_.controlThread = ControlThread()
    global_.controlThread.start()

    sys.exit(app.exec_())
