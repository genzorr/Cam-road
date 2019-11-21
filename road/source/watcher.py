import sys, time, threading, serial
# from mbee import serialstar
from lib.data_classes import *
from lib.motor_controller import *
from lib.data_parser import *
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
        self.off()

    def off(self):
        print('############  Writer stopped  #############')

#-------------------------------------------------------------------------------------#
""" Used to control the motor by Motor_controller class """
class Motor_thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.name = 'Motor'
        self.controller = Controller()
        #   Indicator initialization
        if global_.motor:
            self.portex = indicator_init()


    def run(self):
        while self.alive:
            if global_.motor and self.controller.t % 10 == 0:
                indicate(self.controller.motor.readV(), self.portex)

            # FIXME: needed lock here?

            if global_.motor:
                self.controller.motor.dstep = self.controller.control()
            else:
                value = self.controller.control()

        self.off()


    def off(self):
        if global_.motor:
            indicator_off(self.portex)
            self.controller.off()
        print('############  Motor released  #############')

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
            # with global_.lock:
            #     self.update_host_to_road()
            # with global_.lock:
            #     self.update_road_to_host()
            # with global_.lock:
            #     self.update_special()

            if global_.motor_thread.alive:
                # Check accelerometer data.
                [x, y, z] = self.accel.getdata()
                thr = 5
                if (x > thr) or (z > thr):
                    global_.motor_thread.controller.HARD_STOP = 1
                    print('got')
                    print(x," ", y," ", z)

                # Get data for printing.
                with global_.lock:
                    data = global_.motor_thread.controller.get_data()
                    if (data == None):
                        data = (0,0,0,0,0,0,'')

                    if global_.writer.alive:
                        global_.writer.out = stringData.format(*data)

        self.off()

    def off(self):
        print('############  Watcher stopped  ############')


    # def update_host_to_road(self):
    #     global_.motor_thread.controller.accel = global_.hostData.acceleration
    #     global_.motor_thread.controller.braking = global_.hostData.braking
    #     est_speed = global_.hostData.velocity
    #     global_.motor_thread.controller.mode = global_.hostData.mode
    #     direction = global_.hostData.direction
    #     global_.motor_thread.controller.set_base = global_.hostData.set_base

    #     if not global_.motor_thread.controller.is_braking:
    #         global_.motor_thread.controller.est_speed = est_speed * global_.VELO_MAX / 100

    #     if global_.motor_thread.controller.mode == 2:
    #         global_.motor_thread.controller.direction = direction

    #     if global_.motor_thread.controller.set_base == 1 and not global_.motor_thread.controller.base1_set:
    #         global_.motor_thread.controller.base1 = global_.motor_thread.controller.coordinate
    #     elif global_.motor_thread.controller.set_base == 2 and not global_.motor_thread.controller.base2_set:
    #         global_.motor_thread.controller.base2 = global_.motor_thread.controller.coordinate

    #     return

    # def update_road_to_host(self):
    #     global_.roadData.mode = global_.motor_thread.controller.mode
    #     global_.roadData.coordinate = global_.motor_thread.controller.coordinate
    #     global_.roadData.RSSI = global_.mbee_thread.mbee_data.RSSI
    #     global_.roadData.voltage = global_.mbee_thread.mbee_data.voltage
    #     global_.roadData.current = global_.mbee_thread.mbee_data.current
    #     global_.roadData.temperature = global_.mbee_thread.mbee_data.temperature
    #     global_.roadData.base1 = global_.motor_thread.controller.base1
    #     global_.roadData.base2 = global_.motor_thread.controller.base2

    # def update_special(self):
    #     pass

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
        timeout=0.2
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
