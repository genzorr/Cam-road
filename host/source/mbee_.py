import binascii
import struct
import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

import global_
import serialstar
from global_ import get_logger
from lib.data_classes import HTRData, RTHData, HBData


# Checks some global parameters.
def update_road_to_host():
    if not global_.roadData.base1_set and not global_.roadData.base2_set:
        global_.specialData.end_points_reset = False
    if global_.roadData.mode == -1:
        global_.specialData.motor = False


# MBee radio communication.
class MBeeThread(QThread):
    RSSI_signal = pyqtSignal(float)     # This signal is used to update signal value in application.

    def stop_time_slot(self, value):
        self.stop_time = value

    def __init__(self, port='/dev/ttySAC4', baudrate=230400):
        QThread.__init__(self)
        self.alive = True   # Shows that thread is alive.
        self.logger = get_logger('MBee')    # Thread logger.

        # These values are used to provide self-testing.
        self.self_test = 0
        self.test_local = 1
        self.test_remote = 1

        self.t = 0
        self.t_prev = 0
        self.received_t = 0
        self.stop_time = 0
        self.RSSI = None
        global_.window.telemetryWidget.ui.stop_time.valueChanged.connect(self.stop_time_slot)

        self.package_host = HTRData()
        self.package_special = HBData()
        global_.newHTR = False
        self.special_t = 0

        # Initialization.
        try:
            self.dev = serialstar.SerialStar(port, baudrate, 0.1)
            self.logger.info('# MBee OK')

            # Callback-functions registering.
            self.dev.callback_registring("81", self.frame_81_received)
            self.dev.callback_registring("87", self.frame_87_received)
            self.dev.callback_registring("88", self.frame_88_received)
            self.dev.callback_registring("8C", self.frame_8C_received)
            '''
            # self.dev.callback_registring("83", self.frame_83_received)
            # self.dev.callback_registring("89", self.frame_89_received)
            # self.dev.callback_registring("8A", self.frame_8A_received)
            # self.dev.callback_registring("8B", self.frame_8B_received)
            # self.dev.callback_registring("8F", self.frame_8F_received)
            # self.dev.callback_registring("97", self.frame_97_received)
            '''

            # Sets needed settings for this MBee module.
            self.mbee_init_settings()

        except BaseException:
            self.dev = None
            self.alive = False
            self.logger.warning('# MBee init failed')
            return

    def run(self):
        if not self.dev:
            return

        # Run tests and check results.
        self.run_self_test()
        if (self.test_local == 0) or (self.test_remote == 0):
            self.alive = False
        else:
            self.logger.info('# Tests passed')

        while self.alive:
            self.t = time.time()
            # Transmit and receive data.
            global_.mutex.tryLock(timeout=1)
            self.dev.run()
            global_.mutex.unlock()
            self.transmit()

            # Check if connection is ok.
            if (self.t - self.received_t > 3): #self.stop_time):
                self.logger.warning('# MBee connection lost')
                self.RSSI = None

            # Flush dev buffers.
            if (self.t - self.t_prev) > 3:
                self.t_prev = self.t
                self.dev.ser.flush()

            time.sleep(0.01)
        self.off()

    # Close serial device.
    def off(self):
        if self.dev:
            self.dev.ser.close()
            self.dev = None

    # Transmit packages.
    def transmit(self):
        t = time.time()
        newHTR, newHB = False, False    # Flags that show that data is new.

        # Update flags values.
        global_.mutex.tryLock(timeout=1)
        newHTR = global_.newHTR
        global_.newHTR = False

        # Update packages to be transferred.
        if newHTR:
            self.package_host = global_.hostData
        if t - self.special_t > 1:
            self.special_t = t
            self.package_special = global_.specialData
            newHB = True
        global_.mutex.unlock()

        # Send packages.
        if newHTR and (self.package_host is not None):
            self.dev.send_tx_request('00', global_.TX_ADDR_HOST, self.encrypt_package(self.package_host), '11')
            global_.hostData.direction = 0
            global_.hostData.mode = -1
            global_.hostData.set_base = 0
        if (newHB or newHTR) and (self.package_special is not None):
            self.dev.send_tx_request('00', global_.TX_ADDR_HOST, self.encrypt_package(self.package_special), '11')
            global_.specialData.soft_stop = False

    # Run command on MBee device.
    def command_run(self, command, params):
        frame_id = '00' if params else '01'
        # Send command and save it to memory.
        self.dev.send_immidiate_apply_and_save_local_at(frame_id=frame_id, at_command=command, at_parameter=params)
        self.dev.send_immidiate_apply_and_save_local_at(frame_id='00', at_command='AC', at_parameter='')

        if not params:  # If there are no params, receive package and print result.
            frame = self.dev.run()
            if frame['FRAME_TYPE'] != '81':
                self.logger.info('frame {:2s}: AT-{:2s} {:10s}'.format(frame['FRAME_TYPE'], frame['AT_COMMAND'],
                                                                       frame['AT_PARAMETER_HEX']))

    # Set MBee device init settings: frequency and power.
    def mbee_init_settings(self):
        frequency = global_.settings['FREQUENCY']
        power = global_.settings['POWER']

        PL = {'-32': '00', '-6': '30', '-3': '02', '0': '04', '1': '05', '3': '06', '4': '21', '5': '09', '6': '0A',
              '7': '0B', '8': '0D', '9': '0F', '10': '19', '11': '1A', '12': '23', '13': '1D', '14': '1F', '15': '33',
              '16': '25', '17': '34', '18': '27', '19': '6C', '20': '6B'}

        self.command_run('CF', '{:x}'.format(int(frequency)))
        self.command_run('PL', PL[str(power)])

        self.command_run('CH', '')
        self.command_run('CF', '')
        self.command_run('PL', '')

        self.logger.info('# MBee settings passed to device')
        pass

    # Run self-testing.
    def run_self_test(self):
        # Test 1: local
        self.self_test = 1
        test_time = time.time()

        while (time.time() - test_time) < 5:
            self.dev.send_immidiate_apply_local_at('01', 'MY')
            self.dev.run()

            if self.self_test == 0:
                self.test_local = 1
                break

        if self.self_test == 1:
            self.logger.warning('# No module')
            self.test_local = 0

        # Test 2: remote
        self.self_test = 1
        test_time = time.time()

        while self.alive:
            self.dev.send_tx_request('00', global_.TX_ADDR_HOST, '0000', '10')
            self.dev.run()

            if self.self_test == 0:
                break

            dt = time.time() - test_time
            if (int(dt) > 5):
                test_time = time.time()
                self.logger.info('# Waiting for MBee receiver...')

        if self.self_test == 1:
            self.logger.warning('# No remote module')
            self.test_remote = 0

    # --------------------------------------------------
    # Callback functions.

    def frame_81_received(self, package):
        data = self.decrypt_package(package['DATA'])
        if isinstance(data, RTHData):
            global_.mutex.tryLock(timeout=5)
            global_.roadData = data
            update_road_to_host()
            global_.mutex.unlock()
            self.RSSI = package['RSSI']
            self.received_t = time.time()
        pass

    def frame_83_received(self, package):
        pass

    def frame_87_received(self, package):
        if self.self_test == 1:
            self.self_test = 0
        pass

    def frame_88_received(self, package):
        pass

    def frame_89_received(self, package):
        pass

    def frame_8A_received(self, package):
        pass

    def frame_8B_received(self, package):
        pass

    def frame_8C_received(self, package):
        if self.self_test == 1:
            self.self_test = 0
        pass

    def frame_8F_received(self, package):
        pass

    def frame_97_received(self, package):
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
                package.temperature = hex_to_float(data[24:32])
                package.base1 = hex_to_float(data[32:40])
                package.base2 = hex_to_float(data[40:48])
                package.base1_set = hex_to_bool(data[48:50])
                package.base2_set = hex_to_bool(data[50:52])
                package.direction = hex_to_int(data[52:60])
                package.bases_init_swap = hex_to_bool(data[60:62])

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
                package.motor = hex_to_bool(data[16:18])
                package.lock_buttons = hex_to_bool(data[18:20])
                package.signal_behavior = hex_to_int(data[20:28])

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
            data += float_to_hex(package.temperature)
            data += float_to_hex(package.base1)
            data += float_to_hex(package.base2)
            data += bool_to_hex(package.base1_set)
            data += bool_to_hex(package.base2_set)
            data += int_to_hex(package.direction)
            data += bool_to_hex(package.bases_init_swap)

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
            data += bool_to_hex(package.motor)
            data += bool_to_hex(package.lock_buttons)
            data += int_to_hex(package.signal_behavior)

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
