import sys, os, struct
import threading
import global_
from mbee import serialstar
from lib.data_classes import *


def frame_81_received(package):
    pass
    # print("Received 81-frame.")
    # print(package)

def frame_83_received(package):
    pass
    # print("Received 83-frame.")
    # print(package)

def frame_87_received(package):
    pass
    # print("Received 87-frame.")
    # print(package)

def frame_88_received(package):
    pass
    # print("Received 88-frame.")
    # print(package)

def frame_89_received(package):
    pass
    # print("Received 89-frame.")
    # print(package)

def frame_8A_received(package):
    pass
    # print("Received 8A-frame.")
    # print(package)

def frame_8B_received(package):
    pass
    # print("Received 8B-frame.")
    # print(package)

def frame_8C_received(package):
    pass
    # print("Received 8C-frame.")
    # print(package)

def frame_8F_received(package):
    data = decrypt_package(package['DATA'])
    if isinstance(data, HTRData):
        with global_.lock:
            global_.hostData = data
    if isinstance(data, HBData):
        with global_.lock:
            global_.specialData = data


def frame_97_received(package):
    pass
    # print("Received 97-frame.")
    # print(package)


class Mbee_thread(threading.Thread):
    def __init__(self, port='/dev/ttyS2', baudrate=19200):
        super().__init__()
        self.alive = True
        self.name = 'MBee'
        self.mbee_data = Mbee_data()

        global_.dev = serialstar.SerialStar(port, baudrate)

        #  Callback-functions registering.
        global_.dev.callback_registring("81", frame_81_received)
        global_.dev.callback_registring("83", frame_83_received)
        global_.dev.callback_registring("87", frame_87_received)
        global_.dev.callback_registring("88", frame_88_received)
        global_.dev.callback_registring("89", frame_89_received)
        global_.dev.callback_registring("8A", frame_8A_received)
        global_.dev.callback_registring("8B", frame_8B_received)
        global_.dev.callback_registring("8C", frame_8C_received)
        global_.dev.callback_registring("8F", frame_8F_received)
        global_.dev.callback_registring("97", frame_97_received)

    def run(self):
        while self.alive:
            # Receive
            frame = global_.dev.run()

            # Transmit
            global_.dev.send_tx_request('01', '0001', '012345')

            # Receiving
            # with global_.serial_lock:
            # package = get_decrypt_package(global_.dev)
            # if isinstance(package, HTRData):
            #     with global_.lock:
            #         global_.hostData = package
            # if isinstance(package, HBData):
            #     with global_.lock:
            #         global_.specialData = package

            # # Transmitting
            # with global_.lock:
            #     package = global_.roadData
            # with global_.serial_lock:
            #     if package:
            #         global_.dev.write(encrypt_package(package))

            ##  Other method
            # tmp = self.dev.read(30)
            # if tmp:
            #     buff += tmp
            #     # print('data read')
            #     package = decrypt_data(buff)
            # tmp = None

        self.off()

    def off(self):
        if global_.dev:
            with global_.serial_lock:
                global_.dev.ser.close()
                global_.dev = None
        print('############  Mbee closed  ################')


def decrypt_package(package):
    try:
        data = package
        package = None
        package_type = hex_to_int(data[0:8])
        data = data[8:]

        if package_type == 1:
            package = HTRData()
            package.type = 1

            package.acceleration = hex_to_float(data[0:8])
            package.braking = hex_to_float(data[8:16])
            package.velocity = hex_to_float(data[16:24])
            package.mode = hex_to_int(data[24:32])
            package.direction = hex_to_int(data[32:40])
            package.set_base = hex_to_int(data[40:48])

        elif package_type == 2:
            package = RTHData()
            package.type = 2

            package.mode = hex_to_int(data[0:8])
            package.coordinate = hex_to_float(data[8:16])
            package.RSSI = hex_to_float(data[16:24])
            package.voltage = hex_to_float(data[24:32])
            package.current = hex_to_float(data[32:40])
            package.temperature = hex_to_float(data[40:48])
            package.base1 = hex_to_float(data[48:56])
            package.base2 = hex_to_float(data[56:64])

        elif package_type == 3:
            package = HBData()
            package.type = 3

            package.direction = hex_to_int(data[0:8])
            package.soft_stop = hex_to_bool(data[8:10])
            package.end_points = hex_to_bool(data[10:12])
            package.end_points_stop = hex_to_bool(data[12:14])
            package.end_points_reverse = hex_to_bool(data[14:16])
            package.sound_stop = hex_to_bool(data[16:18])
            package.swap_direction = hex_to_bool(data[18:20])
            package.accelerometer_stop = hex_to_bool(data[20:22])
            package.HARD_STOP = hex_to_bool(data[22:24])
            package.lock_buttons = hex_to_bool(data[24:26])

        else:
            print('error: no such package')
            return None

        return package

    except ValueError or IndexError:
        print('error')
        return None
    except struct.error as exc:
        print(data)
        print(exc)
        return None


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
