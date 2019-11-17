import sys, os, struct, time
import threading
import global_
from mbee import serialstar
from lib.data_classes import *

TX_ADDR = '0001'

def frame_81_received(package):
    data = decrypt_package(package['DATA'])
    if isinstance(data, HTRData):
        # print(time.time())
        with global_.lock:
            global_.hostData = data
            update_host_to_road()
        # print(global_.hostData.mode)
    if isinstance(data, HBData):
        # with global_.lock:
        global_.specialData = data
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
    # print(time.time())
    # data = decrypt_package(package['DATA'])
    # if isinstance(data, HTRData):
    #     # print(time.time())
    #     with global_.lock:
    #         global_.hostData = data
    #         update_host_to_road()
    #     # print(global_.hostData.mode)
    # if isinstance(data, HBData):
    #     # with global_.lock:
    #     global_.specialData = data
    pass


def frame_97_received(package):
    pass
    # print("Received 97-frame.")
    # print(package)


def update_host_to_road():
    global_.motor_thread.controller.accel = global_.hostData.acceleration
    global_.motor_thread.controller.braking = global_.hostData.braking
    est_speed = global_.hostData.velocity
    global_.motor_thread.controller.mode = global_.hostData.mode
    direction = global_.hostData.direction
    global_.motor_thread.controller.set_base = global_.hostData.set_base

    if not global_.motor_thread.controller.is_braking:
        global_.motor_thread.controller.est_speed = est_speed * global_.VELO_MAX / 100

    if global_.motor_thread.controller.mode == 2:
        global_.motor_thread.controller.direction = direction

    if global_.motor_thread.controller.set_base == 1 and not global_.motor_thread.controller.base1_set:
        global_.motor_thread.controller.base1 = global_.motor_thread.controller.coordinate
    elif global_.motor_thread.controller.set_base == 2 and not global_.motor_thread.controller.base2_set:
        global_.motor_thread.controller.base2 = global_.motor_thread.controller.coordinate

    return


def update_road_to_host():
    global_.roadData.mode = global_.motor_thread.controller.mode
    global_.roadData.coordinate = global_.motor_thread.controller.coordinate
    global_.roadData.RSSI = global_.mbee_thread.mbee_data.RSSI
    global_.roadData.voltage = global_.mbee_thread.mbee_data.voltage
    global_.roadData.current = global_.mbee_thread.mbee_data.current
    global_.roadData.temperature = global_.mbee_thread.mbee_data.temperature
    global_.roadData.base1 = global_.motor_thread.controller.base1
    global_.roadData.base2 = global_.motor_thread.controller.base2



class Mbee_thread(threading.Thread):
    def __init__(self, port='/dev/ttyS2', baudrate=19200):
        super().__init__()
        self.alive = True
        self.name = 'MBee'
        self.mbee_data = Mbee_data()

        self.t = 0
        self.t_prev = 0

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
            self.dev.send_tx_request('01', TX_ADDR, '00')

            # Flush dev buffers
            self.t = time.time()
            if ((self.t - self.t_prev) > 7):
                self.t_prev = self.t
                self.dev.ser.flush()
                self.dev.ser.reset_input_buffer()
                self.dev.ser.reset_output_buffer()

            # Receiving
            # with global_.serial_lock:
            # package = get_decrypt_package(self.dev)
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
            #         self.dev.write(encrypt_package(package))

            ##  Other method
            # tmp = self.dev.read(30)
            # if tmp:
            #     buff += tmp
            #     # print('data read')
            #     package = decrypt_data(buff)
            # tmp = None

        self.off()

    def off(self):
        if self.dev:
            self.dev.ser.close()
            self.dev = None
        print('############  Mbee closed  ################')


def decrypt_package(package):
    try:
        data = package
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
