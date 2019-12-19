import sys
import threading, signal

import global_
from watcher import *
from mbee_ import Mbee_thread
from lib.data_classes import *

THREADS = []

def handler(signal, frame):
    global THREADS
    for t in THREADS:
        t.alive = False
    sys.exit(0)

#-------------------------------------------------------------------------------------#
def main():
    global THREADS

    ## Variables.
    global_.lock = threading.Lock()
    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    ## Threads.
    global_.motor_thread = MotorThread()
    THREADS.append(global_.motor_thread)

    global_.writer = Writer()
    THREADS.append(global_.writer)

    global_.mbee_thread = MBeeThread()
    THREADS.append(global_.mbee_thread)

    global_.watcher = Watcher()
    THREADS.append(global_.watcher)

    global_.watcher.start()
    global_.writer.start()
    global_.mbee_thread.start()
    global_.motor_thread.start()

    for t in THREADS:
        while True:
            t.join(1000000000)
            if not t.is_alive():
                break

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    main()
