import sys, time, threading, serial
from mbee import serialstar
from data_classes import *
from lib.lsm6ds3 import *

import globals

VELO_MAX = 30

# lock = threading.Lock()
# lock = 0
# globals.hostData = HTRData()
# roadData = RTHData()
# specialData = HBData()


#-------------------------------------------------------------------------------------#

class Writer(threading.Thread):
    def __init__(self, out=''):
        super().__init__()
        self._out = out

    @property
    def out(self):
        return self._out

    @out.setter
    def out(self, string):
        self._out = string

    def run(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            sys.stdout.write(self._out)
            sys.stdout.flush()
            time.sleep(0.2)

#-------------------------------------------------------------------------------------#
class Mbee_thread(threading.Thread):
    def __init__(self, serial_device):
        super().__init__()
        self.dev = serial_device
        self.analyzer = PackageAnalyzer(serial_device)

    def run(self):
        th = threading.currentThread()
        while getattr(th, "do_run", True):

            package = self.analyzer.decrypt_package()
            if package and not globals.lock:
                lock = 1
                globals.hostData = package
                lock = 0
                # with lock:
                #     # if lock.acquire(False):
                #     globals.hostData = package
                # print(globals.hostData.mode)

#-------------------------------------------------------------------------------------#
""" Used to control the motor by Motor_controller class """
class Motor_thread(threading.Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        th = threading.currentThread()
        while getattr(th, "do_run", True):
            # print(self.controller.globals.hostData.mode)
            # FIXME: MOTOR
            # with lock:
            #     if lock.acquire(False):
            #         self.controller.control()
            # self.controller.get_package()
            self.controller.control()

    def update_host_to_road(self):
        self.controller.accel = globals.hostData.acceleration
        self.controller.braking = globals.hostData.braking
        est_speed = globals.hostData.velocity
        self.controller.mode = globals.hostData.mode
        direction = globals.hostData.direction
        self.controller.set_base = globals.hostData.set_base

        if not self.controller.is_braking:
            self.controller.est_speed = est_speed * VELO_MAX / 100

        if self.controller.mode == BUTTONS:
            self.controller.direction = direction

        if self.controller.set_base == 1 and not self.controller.base1_set:
            self.controller.base1 = self.controller.coordinate
        elif self.controller.set_base == 2 and not self.controller.base2_set:
            self.controller.base2 = self.controller.coordinate
        return

#-------------------------------------------------------------------------------------#
""" Used to control all operations """
class Watcher(threading.Thread):
    def __init__(self, motor_thread, writer, serial_device, accel):
        super().__init__()
        self.motor_thread = motor_thread
        self.writer = writer
        self.dev = serial_device
        self.accel = accel

    def run(self):
        stringData = 't:\t{:.2f}\tv:\t{:.2f}\tB1:\t{:.2f}\tB2:\t{:.2f}\tmode:\t{}\tL:\t{:.3f}\t\t{:s}\n'

        th = threading.currentThread()
        while getattr(th, "do_run", True):

            # data = serial_recv(self.dev, 60)
            # self.motor_thread.controller.data = data # old
            # package = self.analyzer.decrypt_package()
            # if package:
            #     globals.hostData = package

            # Updating motor controller data
            # with lock:
                # if lock.acquire(False):
                # self.motor_thread.update_host_to_road()
            if not globals.lock:
                lock = 1
                self.motor_thread.update_host_to_road()
                lock = 0

            # Check accelerometer data
            [x, y, z] = self.accel.getdata()
            thr = 5
            if (x > thr) or (z > thr):
                self.motor_thread.controller.HARD_STOP = 1
                print('got')
                print(x," ", y," ", z)

            # Write data to console
            data = (0,0,0,0,0,0,'')
            # with lock:
            #     # if lock.acquire(False):
            #     data = self.motor_thread.controller.get_data()
            if not globals.lock:
                lock = 1
                data = self.motor_thread.controller.get_data()
                lock = 0
            self.writer.out = stringData.format(*data)


    # #   Callback functions for SerialStar
    # def frame_81_received(packet):
    #     print("Received 81-frame.")
    #     print(packet)



#-------------------------------------------------------------------------------------#
#   Serial communication
def serial_init(speed=19200, port='/dev/ttyS2'):
    try:
        dev = serial.Serial(
        port=port,
        baudrate=speed,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1
    )
    except serial.serialutil.SerialException:
        print('Could not open port')
        dev = None

    return dev

def serial_recv(dev, size):
    string = dev.read(size).decode()
    return string

def serial_send(dev, string):
    dev.write(string.encode('utf-8'))
