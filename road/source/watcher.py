import sys, time, threading, serial
# from mbee import serialstar
from lib.data_classes import *
from lib.motor_controller import *
from lib.data_parser import *
from lib.lsm6ds3 import *
from lib.indicator import *
from lib.usound import *

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

            self.controller.update()
            try:
                self.controller.motor.dstep = self.controller.dstep
            # else:
            #     value = self.controller.control()

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
        self.accel.ctrl()

        self.usound = USound()

    def run(self):
        stringData = 't:\t{:.2f}\tv:\t{:.2f}\tB1:\t{:.2f}\tB2:\t{:.2f}\tmode:\t{}\tL:\t{:.3f}\t\t{:s}'

        while self.alive:
            # Usound.
            # print(self.usound.read())
            if (self.usound.read() < 100):
                global_.motor_thread.controller.HARD_STOP = 1

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
                        data = (0,0,0,0,0,0,'',0)

                    if global_.writer.alive:
                        global_.writer.out = stringData.format(*data)+'\t'+str(global_.motor_thread.controller.HARD_STOP)+'\n'#+str(self.usound.read())+'\n'

        self.off()

    def off(self):
        print('############  Watcher stopped  ############')
