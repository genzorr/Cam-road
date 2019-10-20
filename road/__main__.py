import sys
sys.path.append('../fortune-controls/Lib')
import threading, signal

import global_
from watcher import *
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
    global_.mbee_thread_write = None
    global_.mbee_thread_read = None

    ## Variables.
    global_.motor = 0
    global_.lock = threading.Lock()
    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    global_.dev = None
    global_.dev = serial_init()
    global_.serial_lock = threading.Lock()

    ## Threads.
    # global_.mbee_thread_write = Mbee_thread_write()
    # global_.mbee_thread_write.start()
    # THREADS.append(global_.mbee_thread_write)

    global_.mbee_thread_read = Mbee_thread_read()
    global_.mbee_thread_read.start()
    THREADS.append(global_.mbee_thread_read)

    global_.writer = Writer()
    global_.writer.start()
    THREADS.append(global_.writer)

    global_.motor_thread = Motor_thread()
    global_.motor_thread.start()
    THREADS.append(global_.motor_thread)

    global_.watcher = Watcher()
    global_.watcher.start()
    THREADS.append(global_.watcher)

    for t in THREADS:
        while True:
            t.join(1000000000)
            if not t.is_alive():
                break

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    main()
