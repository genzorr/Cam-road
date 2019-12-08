import sys, os, struct, time
import threading
import global_
import binascii
from mbee import serialstar
from lib.data_classes import *

TX_ADDR = '0002'

def frame_81_received(package):
    data = decrypt_package(package['DATA'])
    if isinstance(data, HTRData):
        global_.lock.acquire(blocking=True, timeout=1)
        global_.hostData = data
        update_host_to_road()
        global_.lock.release()
    if isinstance(data, HBData):
        global_.lock.acquire(blocking=True, timeout=1)
        global_.specialData = data
        update_special()
        global_.lock.release()
    # print("Received 81-frame.")
    # print(package)
    pass

def frame_83_received(package):
    # print("Received 83-frame.")
    # print(package)
    pass

def frame_87_received(package):
    if (global_.mbee_thread.self_test == 1):
        global_.mbee_thread.self_test = 0
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
    if (global_.mbee_thread.self_test == 1):
        global_.mbee_thread.self_test = 0
    # print("Received 8C-frame.")
    # print(package)
    pass

def frame_8F_received(package):
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
    # print("Received 8F-frame.")
    pass


def frame_97_received(package):
    # print("Received 97-frame.")
    # print(package)
    pass


def update_host_to_road():
    global_.motor_thread.controller.accel = global_.hostData.acceleration
    global_.motor_thread.controller.braking = global_.hostData.braking
    # global_.motor_thread.controller.est_speed = global_.hostData.velocity * global_.VELO_MAX / 100

    if (global_.hostData.mode == 0):
        global_.motor_thread.controller.est_speed = 0
        if (global_.motor_thread.controller.mode != 0):
            global_.motor_thread.controller.soft_stop = 1
    elif (global_.hostData.mode == 1):
        if (global_.motor_thread.controller.mode == 2):
            print('here')
            global_.motor_thread.controller.reverse = 1
            global_.motor_thread.controller.est_speed = 0
        # if (global_.motor_thread.controller.speed == 0):
        #     global_.motor_thread.controller.est_speed = global_.hostData.velocity * global_.VELO_MAX / 100
        # global_.motor_thread.controller.direction = global_.hostData.direction
    elif (global_.hostData.mode == 2):
        global_.motor_thread.controller.est_speed = global_.hostData.velocity * global_.VELO_MAX / 100
        if (global_.motor_thread.controller.mode == 0):
            if (global_.motor_thread.controller.stopped == 1):
                global_.motor_thread.controller.direction = global_.hostData.direction
            else:
                global_.motor_thread.controller.reverse = 1
                global_.motor_thread.controller.est_speed = 0

    # if (global_.motor_thread.controller.mode == 2):
    #     global_.motor_thread.controller.est_speed = global_.hostData.velocity * global_.VELO_MAX / 100


    if global_.hostData.set_base == 1 and not global_.roadData.base1_set:
        global_.motor_thread.controller.base1 = global_.motor_thread.controller.coordinate
        global_.roadData.base1_set = True
    elif global_.hostData.set_base == 2 and not global_.roadData.base2_set:
        global_.motor_thread.controller.base2 = global_.motor_thread.controller.coordinate
        global_.roadData.base2_set = True

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
    global_.roadData.direction = global_.motor_thread.controller.direction


def update_special():
    if global_.specialData.end_points_reset:
        global_.roadData.base1_set = False
        global_.roadData.base2_set = False
        global_.motor_thread.controller.base1 = 0
        global_.motor_thread.controller.base2 = 0
        global_.motor_thread.controller.base1_set = False
        global_.motor_thread.controller.base2_set = False
    if global_.specialData.HARD_STOP:
        global_.motor_thread.controller.HARD_STOP = 0



class Mbee_thread(threading.Thread):
    def __init__(self, port='/dev/ttyS2', baudrate=19200):
        super().__init__()
        self.alive = True
        self.name = 'MBee'
        self.mbee_data = Mbee_data()

        self.self_test = 0
        self.test_local = 1
        self.test_remote = 1

        self.t = 0
        self.t_prev = 0

        try:
            self.dev = serialstar.SerialStar(port, baudrate, 0.4)
        except BaseException:
            self.dev = None
            self.alive = False


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
        self.run_self_test()
        if (self.test_local == 0) or (self.test_remote == 0):
            self.alive = False
        else:
            print('# Tests passed.')

        while self.alive:
            # Receive
            frame = self.dev.run()

            # Transmit
            package = None
            global_.lock.acquire(blocking=True, timeout=1)
            update_road_to_host()
            package = global_.roadData
            global_.lock.release()

            if package is not None:
                package = encrypt_package(package)
                self.dev.send_tx_request('00', TX_ADDR, package, '10')

            # Flush dev buffers
            self.t = time.time()
            if ((self.t - self.t_prev) > 5):
                self.t_prev = self.t
                self.dev.ser.flush()
                self.dev.ser.reset_input_buffer()
                self.dev.ser.reset_output_buffer()

            # print(global_.motor_thread.controller.direction)

        self.off()

    def off(self):
        if self.dev:
            self.dev.ser.close()
            self.dev = None
        print('############  Mbee closed  ################')


    def run_self_test(self):
        # Test 1: remote
        self.self_test = 1
        test_time = time.time()

        while ((time.time() - test_time) < 5):
            self.dev.send_tx_request('00', TX_ADDR, '0001', '10')
            frame = self.dev.run()

            if self.self_test == 0:
                self.test_remote = 1
                break

        if (self.self_test == 1):
            print('# No remote module.')
            self.test_remote = 0

        # Test 2: local
        self.self_test = 1
        test_time = time.time()

        while (time.time() - test_time) < 5:
            self.dev.send_immidiate_apply_local_at('01', 'MY')
            frame = self.dev.run()

            if self.self_test == 0:
                self.test_local = 1
                break

        if (self.self_test == 1):
            print('# No module.')
            self.test_local = 0



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
            package.voltage = hex_to_float(data[16:24])
            package.current = hex_to_float(data[24:32])
            package.temperature = hex_to_float(data[32:40])
            package.base1 = hex_to_float(data[40:48])
            package.base2 = hex_to_float(data[48:56])
            package.base1_set = hex_to_bool(data[56:58])
            package.base2_set = hex_to_bool(data[58:60])
            package.direction = hex_to_int(data[60:68])

        elif package_type == 3:
            package = HBData()
            package.type = 3

            package.soft_stop = hex_to_bool(data[0:2])
            package.end_points_reset = hex_to_bool(data[2:4])
            package.end_points = hex_to_bool(data[4:6])
            package.end_points_stop = hex_to_bool(data[6:8])
            package.end_points_reverse = hex_to_bool(data[8:10])
            package.sound_stop = hex_to_bool(data[10:12])
            package.swap_direction = hex_to_bool(data[12:14])
            package.accelerometer_stop = hex_to_bool(data[14:16])
            package.HARD_STOP = hex_to_bool(data[16:18])
            package.lock_buttons = hex_to_bool(data[18:20])

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
        data += float_to_hex(package.voltage)
        data += float_to_hex(package.current)
        data += float_to_hex(package.temperature)
        data += float_to_hex(package.base1)
        data += float_to_hex(package.base2)
        data += bool_to_hex(package.base1_set)
        data += bool_to_hex(package.base2_set)
        data += int_to_hex(package.direction)

    elif package.type == 3:
        data += bool_to_hex(package.soft_stop)
        data += bool_to_hex(package.end_points_reset)
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
    h = binascii.hexlify(b).decode('ascii')
    return h

def int_to_hex(i):
    b = struct.pack('>i', i)
    h = binascii.hexlify(b).decode('ascii')
    return h

def float_to_hex(f):
    b = struct.pack('>f', f)
    h = binascii.hexlify(b).decode('ascii')
    return h

def hex_to_bool(b):
    (x,) = struct.unpack('>?', bytes.fromhex(b))
    return x

def hex_to_int(b):
    (x,) = struct.unpack('>i', bytes.fromhex(b))
    return x

def hex_to_float(b):
    (x,) = struct.unpack('>f', bytes.fromhex(b))
    return x
