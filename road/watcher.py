import sys, time, threading, serial
# from mbee import serialstar
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
        self.off()

    def off(self):
        print('############  Writer stopped  ############')

#-------------------------------------------------------------------------------------#
class Mbee_thread_write(threading.Thread):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.name = 'MBee_write'
        self.mbee_data = Mbee_data()
        self.dev_write = serial_init()

    def run(self):
        while self.alive:
            # Transmitting
            package = None
            with global_.lock:
                package = global_.roadData
            if package:
                self.dev_write.write(encrypt_package(package))

            # Receiving
            package = decrypt_package(self.dev_write)
            if isinstance(package, HTRData):
                with global_.lock:
                    global_.hostData = package
            if isinstance(package, HBData):
                with global_.lock:
                    global_.specialData = package

        self.off()

    def off(self):
        print('############  Write closed  ############')


class Mbee_thread_read(threading.Thread):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.name = 'MBee_read'
        self.dev_read = global_.serial_device

    def run(self):
        while self.alive:
            # Receiving
            package = decrypt_package(self.dev_read)
            if isinstance(package, HTRData):
                with global_.lock:
                    global_.hostData = package
            if isinstance(package, HBData):
                with global_.lock:
                    global_.specialData = package

        self.off()

    def off(self):
        print('############  Read closed  ############')


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
            # Write data to console
            data = (0,0,0,0,0,0,'')

            if global_.motor_thread.alive:
                # Update data
                with global_.lock:
                    self.update_host_to_road()

                with global_.lock:
                    self.update_road_to_host()

                with global_.lock:
                    self.update_special()

                # Check accelerometer data
                [x, y, z] = self.accel.getdata()
                thr = 5
                if (x > thr) or (z > thr):
                    global_.motor_thread.controller.HARD_STOP = 1
                    print('got')
                    print(x," ", y," ", z)

                # Get data for printing
                with global_.lock:
                    data = global_.motor_thread.controller.get_data()

            if global_.writer.alive:
                global_.writer.out = stringData.format(*data)

        self.off()

    def off(self):
        print('############  Watcher stopped  ############')

    # #   Callback functions for SerialStar
    # def frame_81_received(packet):
    #     print("Received 81-frame.")
    #     print(packet)

    def update_host_to_road(self):
        global_.motor_thread.controller.accel = global_.hostData.acceleration
        global_.motor_thread.controller.braking = global_.hostData.braking
        est_speed = global_.hostData.velocity
        global_.motor_thread.controller.mode = global_.hostData.mode
        direction = global_.hostData.direction
        global_.motor_thread.controller.set_base = global_.hostData.set_base

        if not global_.motor_thread.controller.is_braking:
            global_.motor_thread.controller.est_speed = est_speed * global_.VELO_MAX / 100

        if global_.motor_thread.controller.mode == BUTTONS:
            global_.motor_thread.controller.direction = direction

        if global_.motor_thread.controller.set_base == 1 and not global_.motor_thread.controller.base1_set:
            global_.motor_thread.controller.base1 = global_.motor_thread.controller.coordinate
        elif global_.motor_thread.controller.set_base == 2 and not global_.motor_thread.controller.base2_set:
            global_.motor_thread.controller.base2 = global_.motor_thread.controller.coordinate
        return

    def update_road_to_host(self):
        global_.roadData.mode = global_.motor_thread.controller.mode
        global_.roadData.coordinate = global_.motor_thread.controller.coordinate
        global_.roadData.RSSI = global_.mbee_thread_write.mbee_data.RSSI
        global_.roadData.voltage = global_.mbee_thread_write.mbee_data.voltage
        global_.roadData.current = global_.mbee_thread_write.mbee_data.current
        global_.roadData.temperature = global_.mbee_thread_write.mbee_data.temperature
        global_.roadData.base1 = global_.motor_thread.controller.base1
        global_.roadData.base2 = global_.motor_thread.controller.base2

    def update_special(self):
        pass

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
        timeout=0
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
