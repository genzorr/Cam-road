import time, struct, binascii
from PyQt5.QtCore import QThread, pyqtSignal
import logging

import global_
from global_ import get_logger
import serialstar
from lib.data_classes import *

TX_ADDR = '0001'

#----------------------------------------------------------------------------------------------#
#   A thread used to operate with MBee.
class MbeeThread(QThread):
    RSSI_signal = pyqtSignal(int)

    def __init__(self, port='/dev/ttySAC4', baudrate=230400):
        QThread.__init__(self)
        self.alive = True
        self.logger = get_logger('MBee')

        self.self_test = 0
        self.test_local = 1
        self.test_remote = 1

        self.t = 0
        self.t_prev = 0
        self.RSSI = 0

        try:
            self.dev = serialstar.SerialStar(port, baudrate, 0.4)
        except BaseException:
            self.dev = None
            self.alive = False
            self.logger.warning('# MBee init failed')
            return

        self.logger.info('# MBee OK')

        if self.dev:
            #  Callback-functions registering.
            self.dev.callback_registring("81", self.frame_81_received)
            # self.dev.callback_registring("83", self.frame_83_received)
            self.dev.callback_registring("87", self.frame_87_received)
            # self.dev.callback_registring("88", self.frame_88_received)
            # self.dev.callback_registring("89", self.frame_89_received)
            # self.dev.callback_registring("8A", self.frame_8A_received)
            # self.dev.callback_registring("8B", self.frame_8B_received)
            self.dev.callback_registring("8C", self.frame_8C_received)
            # self.dev.callback_registring("8F", self.frame_8F_received)
            # self.dev.callback_registring("97", self.frame_97_received)


    def update_road_to_host(self):
        if global_.roadData.mode == global_.hostData.mode:
            global_.hostData.mode = -1
        pass


    def run(self):
        self.run_self_test()
        if (self.test_local == 0) or (self.test_remote == 0):
            self.alive = False

        while self.alive:
            t = time.time()

            # Receive
            global_.mutex.tryLock(timeout=1)
            self.dev.run()
            global_.mutex.unlock()

            self.transmit()
            global_.hostData.mode = -1

            # Flush dev buffers
            self.t = time.time()
            if (self.t - self.t_prev) > 3:
                self.t_prev = self.t
                self.dev.ser.flush()
            #     self.dev.ser.reset_input_buffer()
            #     self.dev.ser.reset_output_buffer()

            # print('MBee', t - time.time())
            time.sleep(0.01)
        self.off()

    def off(self):
        if self.dev:
            self.dev.ser.close()
            self.dev = None


    def transmit(self):
        global_.mutex.tryLock(timeout=5)
        package_host = global_.hostData
        package_special = global_.specialData
        global_.mutex.unlock()

        if package_host is not None:
            self.dev.send_tx_request('00', TX_ADDR, self.encrypt_package(package_host), '11')
        if package_special is not None:
            self.dev.send_tx_request('00', TX_ADDR, self.encrypt_package(package_special), '11')

    def run_self_test(self):
        if not self.dev:
            return
        # Test 1: remote
        self.self_test = 1
        test_time = time.time()

        while (time.time() - test_time) < 5:
            self.dev.send_tx_request('00', TX_ADDR, '0001', '10')
            self.dev.run()

            if self.self_test == 0:
                break

        if self.self_test == 1:
            self.logger.warning('# No remote module.')
            self.test_remote = 0

        # Test 2: local
        self.self_test = 1
        test_time = time.time()

        while (time.time() - test_time) < 5:
            self.dev.send_immidiate_apply_local_at('01', 'MY')
            self.dev.run()

            if self.self_test == 0:
                break

        if self.self_test == 1:
            self.logger.warning('# No module.')
            self.test_local = 0

    #--------------------------------------------------
    # Callback functions.

    def frame_81_received(self, package):
        data = self.decrypt_package(package['DATA'])
        if isinstance(data, RTHData):
            global_.mutex.tryLock(timeout=5)
            global_.roadData = data
            # global_.mbeeThread.update_road_to_host()
            global_.mutex.unlock()
            self.RSSI = package['RSSI']
        # print("Received 81-frame.")
        # print(package)
        pass

    def frame_83_received(self, package):
        # if (global_.mbeeThread.self_test == 1):
        #     global_.mbeeThread.self_test = 0
        # print("Received 83-frame.")
        # print(package)
        pass

    def frame_87_received(self, package):
        if self.self_test == 1:
            self.self_test = 0
        # print("Received 87-frame.")
        # print(package)
        pass

    def frame_88_received(self, package):
        # print("Received 88-frame.")
        # print(package)
        pass

    def frame_89_received(self, package):
        # print("Received 89-frame.")
        # print(package)
        pass

    def frame_8A_received(self, package):
        # print("Received 8A-frame.")
        # print(package)
        pass

    def frame_8B_received(self, package):
        # print("Received 8B-frame.")
        # print(package)
        pass

    def frame_8C_received(self, package):
        if self.self_test == 1:
            self.self_test = 0
        # print("Received 8C-frame.")
        # print(package)
        pass

    def frame_8F_received(self, package):
        # print("Received 8F-frame.")
        # print(package)
        pass

    def frame_97_received(self, package):
        # print("Received 97-frame.")
        # print(package)
        pass

    # --------------------------------------------------
    # Data encryption and decryption.

    def decrypt_package(self, package):
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
                self.logger.warning('error: no such package')
                return None

            return package

        except ValueError or IndexError:
            self.logger.warning('error')
            return None
        except struct.error as exc:
            self.logger.warning(data)
            self.logger.warning(exc)
            return None


    def encrypt_package(self, package):
        if not package:
            return None

        data = str()
        data += int_to_hex(package.type)

        if package.type == 1:
            self.logger.debug("Encrypt pack type 1 : \n" + str(package.__dict__))
            data += float_to_hex(package.acceleration)
            data += float_to_hex(package.braking)
            data += float_to_hex(package.velocity)
            data += int_to_hex(package.mode)
            data += int_to_hex(package.direction)
            data += int_to_hex(package.set_base)

        elif package.type == 2:
            self.logger.debug("Encrypt pack type 2")
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
            self.logger.debug("Encrypt pack type 3 : \n" + str(package.__dict__))
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
