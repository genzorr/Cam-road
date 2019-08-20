import time, struct, global_
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from x4motor import X4Motor

DESCR1 = struct.pack('B', 0x7e)
DESCR2 = struct.pack('B', 0xa5)

#-------------------------------------------------------------------------------------#
#   Settings
config = {'id': 1,\
        'Mode': 'Angle',\
        'PWM_Limit' : 300,\
        'PWM_inc_limit' : 2,\
        'I_limit': 5.0,\
        'V_min': 12.0,\
        'Angle_PID_P' : 100,\
        'Angle_PID_I' : 1,\
        'Speed_PID_P' : 100,\
        'Speed_PID_I' : 100,\
        'StepsPerMM': 210,\
        'TimeOut' : 1000,\
        'TempShutDown' : 75,\
        'Reverse': 0}           #   210 - 1step = 0.01m

#----------------------------------------------------------------------------------------------#
#   Keeps 'host-to-road' data
class HTRData():
    def __init__(self):
        self.type = 1

        self.acceleration = 0.0
        self.braking = 0.0
        self.velocity = 0.0
        # FIXME: needed?
        self.mode = 0
        self.direction = 0
        self.set_base = 0
        self.crc = 0

        # Size of package without descriptors and type
        self.size = 4 * 7


#----------------------------------------------------------------------------------------------#
#   Keeps 'road-to-host' data
class RTHData():
    def __init__(self):
        self.type = 2

        self.mode = 0
        self.coordinate = 0.0
        self.RSSI = 0.0
        self.voltage = 0.0
        self.current = 0.0
        self.temperature = 0.0
        self.base1 = 0.0
        self.base2 = 0.0

        self.crc = 0
        # Size of package without descriptors and type
        self.size = 4 * 9

#----------------------------------------------------------------------------------------------#
#   Keeps host's buttons data
class HBData():
    def __init__(self):
        self.type = 3

        self.direction = 0
        self.soft_stop = 0
        self.end_points = 0
        self.end_points_stop = 0
        self.end_points_reverse = 0
        self.sound_stop = 0
        self.swap_direction = 0
        self.accelerometer_stop = 0
        self.HARD_STOP = 0
        self.lock_buttons = 0

        self.crc = 0
        # Size of package without descriptors and type
        self.size = 4 * 11

#----------------------------------------------------------------------------------------------#
STOP = 0
COURSING = 1
BUTTONS = 2

class Controller:
    def __init__(self):
        # FIXME: MOTOR
        print("Motor connection...")
        self.client = ModbusClient(method = "rtu", port="/dev/ttyS1", stopbits = 1,
                             bytesize = 8, parity = 'N', baudrate= 115200,
                             timeout = 0.8, strict=False )

        #   Try to connect to modbus client
        client_status = self.client.connect()

        #   Motor initialization
        self.motor = X4Motor(self.client, settings = config)
        print("OK") if client_status and self.motor else print("Failed")

        #   Print all registers
        registers = self.motor.readAllRO()
        print(registers)

        self.starttime = time.time()
        # self.data = ''

        self.t = 0.0
        self.t_prev = 0.0

        self._speed = 0.0
        self._accel = 0.0
        self._braking = 0.0
        self.AB_choose = 0
        self._est_speed = 0.0
        self._HARD_STOP = 0

        self.coordinate = 0

        self.mode = 0
        self.direction = 1
        self.change_direction = 0
        self.is_braking = 0

        self._base1 = 0.0
        self._base2 = 0.0
        self.set_base = 1
        self.base1_set = 0
        self.base2_set = 0

    def off(self):
        self.motor.release()             # Release motor
        self.client.close()

    @property
    def HARD_STOP(self):
        return self._HARD_STOP

    @HARD_STOP.setter
    def HARD_STOP(self, value):
        self._HARD_STOP = value
        if value == 1:
            self._speed = 0
            self._est_speed = 0

    @property
    def accel(self):
        return self._accel

    @accel.setter
    def accel(self, value):
        if value is not None:
            self._accel = value

    @property
    def braking(self):
        return self._braking

    @braking.setter
    def braking(self, value):
        if value is not None:
            self._braking = value

    @property
    def est_speed(self):
        return self._est_speed

    @est_speed.setter
    def est_speed(self, value):
        if value is not None:
            self._est_speed = min(value, global_.VELO_MAX)

            if value < self.speed:
                self.AB_choose = -1
            elif value > self.speed:
                self.AB_choose = 1
            # else:
            #     self.AB_choose = 0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value is not None:
            if self.AB_choose > 0:
                if value < self.est_speed:
                    self._speed = value
                else:
                    self._speed = self.est_speed
                    self.AB_choose = 0
                # self._speed = min(value, self.est_speed)

            elif self.AB_choose < 0:
                if value > self.est_speed:
                    self._speed = value
                else:
                    self._speed = self.est_speed
                    self.AB_choose = 0
                # self._speed = max(value, self.est_speed)

            else:
                pass

    @property
    def base1(self):
        return self._base1

    @base1.setter
    def base1(self, value):
        if (value > self._base2) and (self.base2 != 0):
            self._base1 = self._base2
            self._base2 = value
            self.base2_set = 1
            self.base1_set = 1
        else:
            self._base1 = value
            self.base1_set = 1

    @property
    def base2(self):
        return self._base2

    @base2.setter
    def base2(self, value):
        if (value < self.base1):# and (self.base1 != 0):
            self._base2 = self._base1
            self._base1 = value
            self.base1_set = 1
            self.base2_set = 1
        else:
            self._base2 = value
            self.base2_set = 1

    def get_data(self):
        # Print message
        if self.direction == 1:
            tmp = "+"
        elif self.direction == -1:
            tmp = "-"
        else:
            tmp = " "
        return (self.t, self.speed, self.base1, self.base2, self.mode, self.coordinate, tmp)


    """ Updates speed by given acceleration """
    def calc_dstep(self, speed_to):
        dt = self.t - self.t_prev
        if self.AB_choose == 0:
            speed_new = self.speed
        elif self.AB_choose > 0:
            speed_new = min(self.speed + self.accel * dt, speed_to)
        else:
            speed_new = max(self.speed - self.braking * dt, speed_to)

        l = (self.speed + speed_new) / 2 * dt * self.direction
        self.speed = speed_new
        return l


    """ Returns motor dstep value """
    def control(self):
        speed = self.speed
        coord = self.coordinate
        braking = self.braking

        # Update time
        self.t_prev = self.t
        self.t = time.time() - self.starttime

        if self.HARD_STOP == 1:
            # No moving if hard stop is enabled
            if (self.speed == 0):
                self.mode = 0
                self.HARD_STOP = 0
            pass
        elif self.mode == STOP and self.speed == 0:
            pass
        else:
            if self.mode == STOP:
                #   Braking if S was pressed
                dstep = self.calc_dstep(speed_to=0)

            elif self.mode == COURSING:
                #   In this mode road will be coursing between two bases

                #   Consider braking into bases points
                if (self.base1_set == 1) and (self.base2_set == 1):
                    if self.direction == -1:
                        dist_to_base = coord - self.base1
                    else:
                        dist_to_base = self.base2 - coord

                    braking_dist = speed * speed / (2 * braking) # if braking != 0 else 0
                    if dist_to_base <= braking_dist:
                        self.is_braking = 1
                        self.est_speed = 0
                        dstep = self.calc_dstep(speed_to=0)

                        # FIXME: seems strange, I should change direction when JUST stopped
                        if dist_to_base < abs(dstep):
                            dstep = dist_to_base * self.direction
                            self.direction = -self.direction
                            self.change_direction = 1 if self.change_direction == 0 else 0
                        else:
                            pass
                    else:
                        self.is_braking = 0
                        dstep = self.calc_dstep(speed_to=self.est_speed)
                else:
                    dstep = self.calc_dstep(speed_to=self.est_speed)

            elif self.mode == BUTTONS:
                dstep = self.calc_dstep(speed_to=self.est_speed)
            else:
                dstep = 0

            self.coordinate += dstep
            # FIXME: MOTOR
            return dstep
        return 0


        # old finction
    def get_package(self):
        try:
            if self.data != '':
                start = self.data.find('255')
                end = self.data.find('254', start+3, len(self.data))

                if (end != -1) and (start != -1):
                    self.data = self.data[start+3:end]
                else:
                    return

                temp = self.data.split(' ')
                est_speed, self.accel, self.braking, self.mode, direction, self.set_base = \
                float(temp[0]), float(temp[1]), float(temp[2]), int(temp[3]), int(temp[4]), int(temp[5])

                if not self.is_braking:
                    self.est_speed = est_speed

                if self.mode > 2:
                    self.mode = 0
                self.accel = 3
                self.braking = 3

                # direction field: -1 if moving left, +1 if right, 0 if stop
                if self.mode == BUTTONS:
                    self.direction = direction

                if self.set_base == 1 and not self.base1_set:
                    self.base1 = self.coordinate
                elif self.set_base == 2 and not self.base2_set:
                    self.base2 = self.coordinate

                self.data = ''

        except ValueError:
            print('error')
        except IndexError:
            print('error')
        return
#----------------------------------------------------------------------------------------------#
class Mbee_data:
    def __init__(self):
        self.RSSI = 0
        self.voltage = 0
        self.current = 0
        self.temperature = 0

#----------------------------------------------------------------------------------------------#

class PackageAnalyzer:
    def __init__(self, serial_device):
        self.dev = serial_device

    def encrypt_package(self, package):
        data = bytes()
        data += DESCR1
        data += DESCR2
        data += int_to_bytes(package.type)

        if package.type == 1:
            data += float_to_bytes(package.acceleration)
            data += float_to_bytes(package.braking)
            data += float_to_bytes(package.velocity)
            data += int_to_bytes(package.mode)
            data += int_to_bytes(package.direction)
            data += int_to_bytes(package.set_base)
            package.crc = package.acceleration + package.braking + package.velocity + \
                          package.mode + package.direction + package.set_base

        elif package.type == 2:
            data += int_to_bytes(package.mode)
            data += float_to_bytes(package.coordinate)
            data += float_to_bytes(package.RSSI)
            data += float_to_bytes(package.voltage)
            data += float_to_bytes(package.current)
            data += float_to_bytes(package.temperature)
            data += float_to_bytes(package.base1)
            data += float_to_bytes(package.base2)
            package.crc = package.mode + package.coordinate + package.RSSI + \
                          package.voltage + package.current + package.temperature + \
                          package.base1 + package.base2

        elif package.type == 3:
            data += int_to_bytes(package.direction)
            data += int_to_bytes(package.soft_stop)
            data += int_to_bytes(package.end_points)
            data += int_to_bytes(package.end_points_stop)
            data += int_to_bytes(package.end_points_reverse)
            data += int_to_bytes(package.sound_stop)
            data += int_to_bytes(package.swap_direction)
            data += int_to_bytes(package.accelerometer_stop)
            data += int_to_bytes(package.HARD_STOP)
            data += int_to_bytes(package.lock_buttons)
            package.crc = package.direction + package.soft_stop + package.end_points + \
                          package.end_points_stop + package.end_points_reverse + package.sound_stop + \
                          package.swap_direction + package.accelerometer_stop + package.HARD_STOP + package.lock_buttons

        else:
            return None

        data += float_to_bytes(package.crc)
        return data


    def decrypt_package(self):
        try:
            while global_.mbee_thread.alive:
                descr1 = self.dev.read(1)
                descr2 = self.dev.read(1)

                if descr1 != DESCR1 and descr2 != DESCR2:
                    if descr2 == DESCR1:
                        descr1 = DESCR1
                        descr2 = self.dev.read(1)

                        if descr2 == DESCR2:
                            break

                    # print("Bad index", descr1, descr2)
                else: break

            crc = 0
            type = bytes_to_int(self.dev.read(4))

            if type == 1:
                package = HTRData()
                package.type = 1

                data = self.dev.read(package.size)
                if len(data) < package.size:
                    return None

                package.acceleration = bytes_to_float(data[0:4])
                package.braking = bytes_to_float(data[4:8])
                package.velocity = bytes_to_float(data[8:12])
                package.mode = bytes_to_int(data[12:16])
                package.direction = bytes_to_int(data[16:20])
                package.set_base = bytes_to_int(data[20:24])
                crc = package.acceleration + package.braking + package.velocity + \
                        package.mode + package.direction + package.set_base
                package.crc = bytes_to_float(data[24:28])
                if package.crc != crc:
                    print('Bad crc 1')
                    return None

            elif type == 2:
                package = RTHData()
                package.type = 2

                data = self.dev.read(package.size)
                if len(data) < package.size:
                    return None

                package.mode = bytes_to_int(data[0:4])
                package.coordinate = bytes_to_float(data[4:8])
                package.RSSI = bytes_to_float(data[8:12])
                package.voltage = bytes_to_float(data[12:16])
                package.current = bytes_to_float(data[16:20])
                package.temperature = bytes_to_float(data[20:24])
                package.base1 = bytes_to_float(data[24:28])
                package.base2 = bytes_to_float(data[28:32])
                crc = package.mode + package.coordinate + package.RSSI + \
                      package.voltage + package.current + package.temperature + \
                      package.base1 + package.base2
                package.crc = bytes_to_float(data[32:36])
                if package.crc != crc:
                    print('Bad crc 2')
                    return None

            elif type == 3:
                package = HBData()
                package.type = 3

                data = self.dev.read(package.size)
                if len(data) < package.size:
                    return None

                package.direction = bytes_to_int(data[0:4])
                package.soft_stop = bytes_to_int(data[4:8])
                package.end_points = bytes_to_int(data[8:12])
                package.end_points_stop = bytes_to_int(data[12:16])
                package.end_points_reverse = bytes_to_int(data[16:20])
                package.sound_stop = bytes_to_int(data[20:24])
                package.swap_direction = bytes_to_int(data[24:28])
                package.accelerometer_stop = bytes_to_int(data[28:32])
                package.HARD_STOP = bytes_to_int(data[32:36])
                package.lock_buttons = bytes_to_int(data[36:40])
                crc = package.direction + package.soft_stop + package.end_points + \
                      package.end_points_stop + package.end_points_reverse + package.sound_stop + \
                      package.swap_direction + package.accelerometer_stop + package.HARD_STOP + package.lock_buttons
                package.crc = bytes_to_float(data[40:44])
                if package.crc != crc:
                    print('Bad crc 3')
                    return None
            else:
                return None

            return package

        except ValueError or IndexError:
            # print('error')
            return None
        except struct.error:
            # print(data)
            return None


def int_to_bytes(i):
    b = struct.pack('=i', i)
    return b

def float_to_bytes(f):
    b = struct.pack('=f', f)
    return b

def bytes_to_int(b):
    (x,) = struct.unpack('=i', b)
    return x

def bytes_to_float(b):
    (x,) = struct.unpack('=f', b)
    return x
