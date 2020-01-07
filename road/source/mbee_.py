import struct, time
import threading
import binascii
import logging
import global_
from global_ import get_logger

import serialstar
from lib.data_classes import *


def update_host_to_road():
    global_.motor_thread.controller.accel = global_.hostData.acceleration * global_.ACCEL_MAX / 100
    global_.motor_thread.controller.braking = global_.hostData.braking * global_.BRAKING_MAX / 100
    if (global_.motor_thread.controller.braking < 1):
        global_.motor_thread.controller.braking = 1


    if global_.hostData.mode == 0:
        if global_.motor_thread.controller.motor:
            global_.motor_thread.controller.clean_motor_error()
        global_.motor_thread.controller.est_speed = 0
        global_.motor_thread.controller.continue_ = 0
        global_.motor_thread.controller.reverse = 0
        if global_.motor_thread.controller.mode != 0:
            global_.motor_thread.controller.soft_stop = 1

    else:
        if global_.hostData.direction != 0:
            if not global_.motor_thread.controller.motor_state:
                global_.motor_thread.controller.direction = global_.hostData.direction
                global_.motor_thread.controller.motor_state = True

            if global_.motor_thread.controller.mode == 0:
                if global_.motor_thread.controller.direction == 0:
                    global_.motor_thread.controller.direction = global_.hostData.direction

                if global_.motor_thread.controller.direction == global_.hostData.direction:
                    global_.motor_thread.controller.continue_ = 1
                else:
                    global_.motor_thread.controller.reverse = 1
                    global_.motor_thread.controller.est_speed = 0

            elif global_.motor_thread.controller.mode == 1:
                if global_.hostData.direction == global_.motor_thread.controller.direction:
                    global_.motor_thread.controller.continue_ = 1

            elif global_.motor_thread.controller.mode == 2:
                if global_.hostData.direction != global_.motor_thread.controller.direction:
                    global_.motor_thread.controller.reverse = 1


    #  Set base points.
    if global_.hostData.set_base == 1 and not global_.roadData.base1_set:
        global_.motor_thread.controller.base1 = global_.motor_thread.controller.coordinate
        global_.roadData.base1_set = True
    elif global_.hostData.set_base == 1 and not global_.roadData.base2_set:
        if (global_.motor_thread.controller.coordinate != global_.motor_thread.controller.base1):
            global_.motor_thread.controller.base2 = global_.motor_thread.controller.coordinate
            global_.roadData.base2_set = True

    return


def update_road_to_host():
    global_.roadData.mode = global_.motor_thread.controller.mode
    global_.roadData.coordinate = global_.motor_thread.controller.coordinate
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
        global_.roadData.bases_init_swap = False

    if global_.specialData.motor:
        global_.motor_thread.controller.motor_state = False
        global_.motor_thread.controller.est_speed = 0
        global_.motor_thread.controller.continue_ = 0
        global_.motor_thread.controller.reverse = 0
        if global_.motor_thread.controller.mode != 0:
            global_.motor_thread.controller.soft_stop = 1

    global_.motor_thread.controller.end_points = global_.specialData.end_points
    global_.motor_thread.controller.end_points_stop = global_.specialData.end_points_stop
    global_.motor_thread.controller.end_points_reverse = global_.specialData.end_points_reverse

    # Signal lost behavior
    global_.motor_thread.signal_behavior = int(global_.specialData.signal_behavior)


class MBeeThread(threading.Thread):
    def __init__(self, port='/dev/ttyS2', baudrate=230400):
        super().__init__()
        self.alive = True
        self.logger = get_logger('MBee')
        self.name = 'MBee'
        self.mbee_data = Mbee_data()

        self.self_test = 0
        self.test_local = 1
        self.test_remote = 1

        self.t = 0
        self.t_prev = 0
        self.received_t = 0

        # Initialization.
        try:
            self.dev = serialstar.SerialStar(port, baudrate, 0.2)
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
            self.transmit()
            self.dev.run()

            # Check if connection is ok.
            if (self.t - self.received_t > 3):
                self.t_prev = self.t
                self.dev.ser.flush()
                if global_.motor_thread.controller.signal_lost_sig_set == False:
                    global_.motor_thread.controller.signal_lost_sig = True
                else:
                    global_.motor_thread.controller.signal_lost_sig = False

                self.logger.warning('# MBee connection lost')
            else:
                global_.motor_thread.controller.signal_lost_sig = False
                global_.motor_thread.controller.signal_lost_sig_set = False

            time.sleep(0.05)

        self.off()

    # Close serial device.
    def off(self):
        if self.dev:
            self.dev.ser.close()
            self.dev = None
        self.logger.info('############  Mbee closed  ################')

    # Transmit packages.
    def transmit(self):
        package = None
        global_.lock.acquire(blocking=True, timeout=1)
        update_road_to_host()
        package = global_.roadData
        global_.lock.release()

        # Send packages.
        if package is not None:
            package = self.encrypt_package(package)
            self.dev.send_tx_request('00', global_.TX_ADDR_ROAD, package, '11')


    def command_run(self, command, params):
        frame_id = '00' if params else '01'
        self.dev.send_immidiate_apply_and_save_local_at(frame_id=frame_id, at_command=command, at_parameter=params)
        self.dev.send_immidiate_apply_and_save_local_at(frame_id='00', at_command='AC', at_parameter='')

        if not params:
            frame = self.dev.run()
            if frame and frame['FRAME_TYPE'] != '81':
                self.logger.info('frame {:2s}: AT-{:2s} {:10s}'.format(frame['FRAME_TYPE'], frame['AT_COMMAND'], frame['AT_PARAMETER_HEX']))

    def mbee_init_settings(self):
        frequency = global_.settings['FREQUENCY']
        power = global_.settings['POWER']

        PL = {'-32':'00', '-6':'30', '-3':'02', '0':'04', '1':'05', '3':'06', '4':'21', '5':'09', '6':'0A',\
                '7':'0B', '8':'0D', '9':'0F', '10':'19', '11':'1A', '12':'23', '13':'1D', '14':'1F', '15':'33',\
                '16':'25', '17':'34', '18':'27', '19':'6C', '20':'6B'}

        self.command_run('CF', '{:x}'.format(int(frequency)))
        self.command_run('PL', PL[str(power)])

        self.command_run('CH', '')
        self.command_run('CF', '')
        self.command_run('PL', '')

        self.logger.info('# MBee settings passed to device')
        pass

    def run_self_test(self):
        if not self.dev:
            return

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

        # Test 1: remote
        self.self_test = 1
        test_time = time.time()

        while self.alive:
            self.dev.send_tx_request('00', global_.TX_ADDR_ROAD, '0000', '10')
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


    def frame_81_received(self, package):
        data = self.decrypt_package(package['DATA'])
        if isinstance(data, HTRData):
            global_.lock.acquire(blocking=True, timeout=1)
            global_.hostData = data
            update_host_to_road()
            global_.lock.release()
            self.received_t = time.time()
        if isinstance(data, HBData):
            global_.lock.acquire(blocking=True, timeout=1)
            global_.specialData = data
            update_special()
            global_.lock.release()
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
                # package.current = hex_to_float(data[24:32])
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
            self.logger.warning('Value/Index error')
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
            data += float_to_hex(package.temperature)
            data += float_to_hex(package.base1)
            data += float_to_hex(package.base2)
            data += bool_to_hex(package.base1_set)
            data += bool_to_hex(package.base2_set)
            data += int_to_hex(package.direction)
            data += bool_to_hex(package.bases_init_swap)

        elif package.type == 3:
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
