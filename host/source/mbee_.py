import sys, os, subprocess, time
import struct
import global_
import threading
from PyQt5.QtCore import QThread, QMutex

from mbee import serialstar
from lib.data_classes import *

TX_ADDR = '0002'


def frame_81_received(package):
    # print("Received 81-frame.")
    # print(package)
    pass

def frame_83_received(package):
    # print("Received 83-frame.")
    # print(package)
    pass

def frame_87_received(package):
    # print("Received 87-frame.")
    # print(package)
    pass

def frame_88_received(package):
    # print("Received 88-frame.")
    # print(package)
    pass

def frame_89_received(package):
    # print("Received 89-frame.")
    # print(package)
    pass

def frame_8A_received(package):
    # print("Received 8A-frame.")
    # print(package)
    pass

def frame_8B_received(package):
    # print("Received 8B-frame.")
    # print(package)
    pass

def frame_8C_received(package):
    # print("Received 8C-frame.")
    # print(package)
    pass

def frame_8F_received(package):
    if (package['SOURCE_ADDRESS_HEX'] == TX_ADDR):
        rssi = package['RSSI']
        global_.roadData.RSSI = rssi
    # print("Received 8F-frame.")
    # print(package)
    pass

def frame_97_received(package):
    # print("Received 97-frame.")
    # print(package)
    pass

#----------------------------------------------------------------------------------------------#
#   A thread used to operate with MBee.
class MbeeThread(QThread):
    def __init__(self, port='/dev/ttySAC4', baudrate=19200):
        QThread.__init__(self)
        self.alive = True
        self.t = 0
        self.t_prev = 0

        # subprocess.call('./radio_off.sh')
        # subprocess.call('./radio_on.sh')

        self.dev = serialstar.SerialStar(port, baudrate, 0.4)

        #  Callback-functions registering.
        self.dev.callback_registring("81", frame_81_received)
        self.dev.callback_registring("83", frame_83_received)
        self.dev.callback_registring("87", frame_87_received)
        self.dev.callback_registring("88", frame_88_received)
        self.dev.callback_registring("89", frame_89_received)
        self.dev.callback_registring("8A", frame_8A_received)
        self.dev.callback_registring("8B", frame_8B_received)
        self.dev.callback_registring("8C", frame_8C_received)
        self.dev.callback_registring("8F", frame_8F_received)
        self.dev.callback_registring("97", frame_97_received)

    def run(self):
        while self.alive:
            # Receive
            # print('receive 1: ', time.time())
            frame = self.dev.run()
            # print('receive 2: ', time.time())

            # Transmit
            global_.mutex.tryLock(timeout=10)
            package = global_.hostData
            global_.mutex.unlock()

            package = encrypt_package(package)
            self.dev.send_tx_request('00', TX_ADDR, package, '11')
            time.sleep(0.2)

            # Flush dev buffers
            self.t = time.time()
            if ((self.t - self.t_prev) > 7):
                self.t_prev = self.t
                self.dev.ser.flush()
                self.dev.ser.reset_input_buffer()
                self.dev.ser.reset_output_buffer()

            # Transmitting.
            # package = self.hostData
            # data = encrypt_package(package)
            # dev.write(data)
            #
            # package = self.specialData
            # data = encrypt_package(package)
            # dev.write(data)

            # # Receiving.
            # package = get_decrypt_package(dev)
            # if isinstance(package, RTHData):
            #     self.roadData = package

            time.sleep(0.3)

        self.off()

    def off(self):
        if self.dev:
            self.dev.ser.close()
            self.dev = None
        pass


def encrypt_package(package):
    if not package:
        return None

    data = str()
    data += int_to_hex(package.type)

    if package.type == 1:
        data += float_to_hex(package.acceleration)
        data += float_to_hex(package.braking)
        data += float_to_hex(package.velocity)
        data += int_to_hex(package.mode)
        data += int_to_hex(package.direction)
        data += int_to_hex(package.set_base)

    elif package.type == 2:
        data += int_to_hex(package.mode)
        data += float_to_hex(package.coordinate)
        data += float_to_hex(package.RSSI)
        data += float_to_hex(package.voltage)
        data += float_to_hex(package.current)
        data += float_to_hex(package.temperature)
        data += float_to_hex(package.base1)
        data += float_to_hex(package.base2)

    elif package.type == 3:
        data += int_to_hex(package.direction)
        data += bool_to_hex(package.soft_stop)
        data += bool_to_hex(package.end_points)
        data += bool_to_hex(package.end_points_stop)
        data += bool_to_hex(package.end_points_reverse)
        data += bool_to_hex(package.sound_stop)
        data += bool_to_hex(package.swap_direction)
        data += bool_to_hex(package.accelerometer_stop)
        data += bool_to_hex(package.HARD_STOP)
        data += bool_to_hex(package.lock_buttons)

    else:
        return None

    return data


def bool_to_hex(c):
    b = struct.pack('>?', c)
    return b.hex()

def int_to_hex(i):
    b = struct.pack('>i', i)
    return b.hex()

def float_to_hex(f):
    b = struct.pack('>f', f)
    return b.hex()

def hex_to_bool(b):
    (x,) = struct.unpack('>?', bytes.fromhex(b))
    return x

def hex_to_int(b):
    (x,) = struct.unpack('>i', bytes.fromhex(b))
    return x

def hex_to_float(b):
    (x,) = struct.unpack('>f', bytes.fromhex(b))
    return x
