import sys, time
sys.path.append('../fortune-controls/Lib')
import threading, signal

from watcher import *
from data_classes import *

THREADS = []

def handler(signal, frame):
    global THREADS
    for t in THREADS:
        t.alive = False
    sys.exit(0)

#-------------------------------------------------------------------------------------#
def main():
    global THREADS

    global_.lock = threading.Lock()
    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    global_.writer = Writer()
    global_.writer.start()

    global_.mbee_thread = Mbee_thread()
    global_.mbee_thread.start()

    global_.motor_thread = Motor_thread()
    global_.motor_thread.start()

    global_.watcher = Watcher()
    global_.watcher.start()

    THREADS.append(global_.mbee_thread)
    THREADS.append(global_.motor_thread)
    THREADS.append(global_.writer)
    THREADS.append(global_.watcher)

    for t in THREADS:
        while True:
            t.join(1000000000)
            if not t.isAlive:
                break
        t.off()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    main()
