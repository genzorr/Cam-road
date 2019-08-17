import sys, time, threading, serial
from lib.lsm6ds3 import *

SPEED_MAX = 20

STOP = 0
COURSING = 1
BUTTONS = 2


#-------------------------------------------------------------------------------------#
#   Host-to-road data
class HTRData():
    def __init__(self):
        self.base1 = 0.0
        self.base2 = 0.0
        self.speed = 0.0
        self.acceleration = 0.0
        self.braking = 0.0

#   Road-to-host data
class RTHData():
    def __init__(self):
        self.voltage = 0.0
        self.current = 0.0
        self.temperature = 0.0
        self.RSSI = 0.0
        self.coordinate = 0.0
        self.speed = 0.0
        self.acceleration = 0.0
        self.braking = 0.0

#-------------------------------------------------------------------------------------#

class Writer(threading.Thread):
    def __init__(self, out=''):
        super().__init__()
        self._out = out

    @property
    def out(self):
        return self._out

    @out.setter
    def out(self, string):
        self._out = string


    def run(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            sys.stdout.write(self._out)
            sys.stdout.flush()
            time.sleep(0.2)

#-------------------------------------------------------------------------------------#

class Motor_control(threading.Thread):
    def __init__(self, motor):
        super().__init__()
        self.motor = motor
        self._data = ''
        self.starttime = time.time()

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
            self._est_speed = min(value, SPEED_MAX)

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
        if (value < self.base1) and (self.base1 != 0):
            self._base2 = self._base1
            self._base1 = value
            self.base1_set = 1
            self.base2_set = 1
        else:
            self._base2 = value
            self.base2_set = 1

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if value is not None:
            self._data = value


    def packageResolver(self):
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


    """ Updates speed by given acceleration """
    def update_motor(self, speed_to):
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
    def controller(self):
        speed = self.speed
        coord = self.coordinate
        braking = self.braking

        if self.HARD_STOP == 1:
            # No moving if hard stop is enabled
            return 0
        elif self.mode == STOP and self.speed == 0:
            return 0
        else:
            if self.mode == STOP:
                #   Braking if S was pressed
                dstep = self.update_motor(speed_to=0)

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
                        dstep = self.update_motor(speed_to=0)

                        # FIXME: seems strange, I should change direction when JUST stopped
                        if dist_to_base < abs(dstep):
                            dstep = dist_to_base * self.direction
                            self.direction = -self.direction
                            self.change_direction = 1 if self.change_direction == 0 else 0
                        else:
                            pass
                    else:
                        self.is_braking = 0
                        dstep = self.update_motor(speed_to=self.est_speed)
                else:
                    dstep = self.update_motor(speed_to=self.est_speed)

            elif self.mode == BUTTONS:
                dstep = self.update_motor(speed_to=self.est_speed)
            else:
                pass

            self.coordinate += dstep
            return dstep


    def run(self):
        th = threading.currentThread()
        while getattr(th, "do_run", True):

            self.packageResolver()
            # FIXME: MOTOR
            # self.motor.dstep = self.controller()
            dstep = self.controller()

            # Update time
            self.t_prev = self.t
            self.t = time.time() - self.starttime

#-------------------------------------------------------------------------------------#

class Watcher(threading.Thread):
    def __init__(self, motor_control, writer, serial_device, accel):
        super().__init__()
        self.motor_control = motor_control
        self.writer = writer
        self.dev = serial_device
        self.accel = accel

    def run(self):
        stringData = 't:\t{:.2f}\tv:\t{:.2f}\tB1:\t{:.2f}\tB2:\t{:.2f}\tmode:\t{}\tL:\t{:.3f}\t\t{:s}\n'

        th = threading.currentThread()
        while getattr(th, "do_run", True):

            data = serial_recv(self.dev, 60)
            self.motor_control.data = data

            [x, y, z] = self.accel.getdata()

            thr = 5
            if (x > thr) or (z > thr):
                self.motor_control.HARD_STOP = 1
                print('got')
                print(x," ", y," ", z)

            # Print message
            if self.motor_control.direction == 1:
                tmp = "+"
            elif self.motor_control.direction == -1:
                tmp = "-"
            else:
                tmp = " "

            data = (self.motor_control.t,
                    self.motor_control.speed, self.motor_control.base1, self.motor_control.base2,
                    self.motor_control.mode, self.motor_control.coordinate, tmp)
            self.writer.out = stringData.format(*data)


#-------------------------------------------------------------------------------------#
#   Serial communication
def serial_init(speed=9600, port='/dev/ttyS2'):
    try:
        dev = serial.Serial(
        port=port,
        baudrate=speed,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1
    )
    except serial.serialutil.SerialException:
        dev = None

    return dev

def serial_recv(dev, size):
    string = dev.read(size).decode()
    return string

def serial_send(dev, string):
    dev.write(string.encode('utf-8'))
