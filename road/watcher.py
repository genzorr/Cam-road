import sys, time, threading, serial
from mbee import serialstar
from data_classes import *
from lib.lsm6ds3 import *
from lib.indicator import *

import global_

#-------------------------------------------------------------------------------------#

class Writer(threading.Thread):
    def __init__(self, out=''):
        super().__init__()
        self.alive = True
        self.name = 'Writer'
        self._out = out

    @property
    def out(self):
        return self._out

    @out.setter
    def out(self, string):
        self._out = string

    def run(self):
        while self.alive:
            sys.stdout.write(self._out)
            sys.stdout.flush()
            time.sleep(0.2)

#-------------------------------------------------------------------------------------#
class Mbee_thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.name = 'MBee'
        self.dev = serial_init()
        self.analyzer = PackageAnalyzer(self.dev)

    def run(self):
        while self.alive:
            package = self.analyzer.decrypt_package()

            if package:
                with global_.lock:
                    global_.hostData = package

        self.off()

    def off(self):
        self.dev.close()
        print('############  Serial port closed  ############')


#-------------------------------------------------------------------------------------#
""" Used to control the motor by Motor_controller class """
class Motor_thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.name = 'Motor'
        self.controller = Controller()
        #   Indicator initialization
        self.portex = indicator_init()


    def run(self):
        while self.alive:
            if self.controller.t % 10 == 0:
                indicate(self.controller.motor.readV(), self.portex)

            # FIXME: needed lock here?
            self.controller.motor.dstep = self.controller.control()

        self.off()


    def update_host_to_road(self):
        self.controller.accel = global_.hostData.acceleration
        self.controller.braking = global_.hostData.braking
        est_speed = global_.hostData.velocity
        self.controller.mode = global_.hostData.mode
        direction = global_.hostData.direction
        self.controller.set_base = global_.hostData.set_base

        if not self.controller.is_braking:
            self.controller.est_speed = est_speed * global_.VELO_MAX / 100

        if self.controller.mode == BUTTONS:
            self.controller.direction = direction

        if self.controller.set_base == 1 and not self.controller.base1_set:
            self.controller.base1 = self.controller.coordinate
        elif self.controller.set_base == 2 and not self.controller.base2_set:
            self.controller.base2 = self.controller.coordinate
        return


    def off(self):
        # FIXME: MOTOR
        indicator_off(self.portex)
        self.controller.off()
        print('##############  Motor released  ##############')

#-------------------------------------------------------------------------------------#
""" Used to control all operations """
class Watcher(threading.Thread):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.name = 'Watcher'
        self.accel = Accelerometer()
        # FIXME: make interrupts
        self.accel.ctrl()

    def run(self):
        stringData = 't:\t{:.2f}\tv:\t{:.2f}\tB1:\t{:.2f}\tB2:\t{:.2f}\tmode:\t{}\tL:\t{:.3f}\t\t{:s}\n'

        while self.alive:
            if global_.motor_thread.alive:
                with global_.lock:
                    global_.motor_thread.update_host_to_road()

            if global_.motor_thread.alive:
                # Check accelerometer data
                [x, y, z] = self.accel.getdata()
                thr = 5
                if (x > thr) or (z > thr):
                    global_.motor_thread.controller.HARD_STOP = 1
                    print('got')
                    print(x," ", y," ", z)

            # Write data to console
            data = (0,0,0,0,0,0,'')

            if global_.motor_thread.alive:
                with global_.lock:
                    data = global_.motor_thread.controller.get_data()

            if global_.writer.alive:
                global_.writer.out = stringData.format(*data)

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
