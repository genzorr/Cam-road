import sys
import threading, signal
import hjson
import os.path as path

import global_
from watcher import *
from mbee_ import MBeeThread
from lib.data_classes import *

THREADS = []

def handler(signal, frame):
    global THREADS
    for t in THREADS:
        t.alive = False
    sys.exit(0)

def get_dir_path():
    filepath = path.abspath(__file__)
    dirname = path.dirname(filepath)
    dirname_parent = path.split(dirname)[0]
    return path.split(dirname_parent)[0]

#-------------------------------------------------------------------------------------#
def main():
    global THREADS

    # Config file data.
    f = open(get_dir_path() + '/config.json')
    config = hjson.loads(f.read())
    global_.ACCEL_MAX = config["ACCEL_MAX"]
    global_.BRAKING_MAX = config["BRAKING_MAX"]
    global_.VELO_MAX = config["VELO_MAX"]
    global_.TX_ADDR_HOST = config["TX_ADDR_HOST"]
    global_.TX_ADDR_ROAD = config["TX_ADDR_ROAD"]
    global_.settings = config

    # Create global data classes.
    global_.lock = threading.Lock()
    global_.hostData = HTRData()
    global_.roadData = RTHData()
    global_.specialData = HBData()

    # Set up threads.
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
