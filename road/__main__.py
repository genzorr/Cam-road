import sys, time
sys.path.append('../fortune-controls/Lib')
import threading, signal

from watcher import *
from data_classes import *
import global_

global NO_MOTOR

def handler(signal, frame):
    print('Ctrl-C.... Exiting')
    for t in global_.THREADS:
        t.alive = False
    sys.exit(0)

#-------------------------------------------------------------------------------------#
def main():
    global_.lock = 0
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

    global_.THREADS = [global_.mbee_thread, global_.motor_thread, global_.writer, global_.watcher]

    for t in global_.THREADS:
        while True:
            t.join(1000000)
            if not t.alive:
                break


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    main()
    # try:
    #     main()

    # except KeyboardInterrupt:
    #     print()

    #     global_.motor_thread.join(10)
    #     global_.writer.join(10)
    #     global_.watcher.join(10)
    #     global_.mbee_thread.join(10)

    #     global_.motor_thread.off()
    #     # while (not watcher.is_alive()) and (not motor_thread.is_alive()) and (not mbee_thread.is_alive()) and (not writer.is_alive()):
    #     #     pass
