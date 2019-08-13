import sys, time, threading, serial
from lib.lsm6ds3 import *

SPEED_MAX = 20

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
            time.sleep(0.5)

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
        self.HARD_STOP = 0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if (self.HARD_STOP == 1):
            self._speed = value
        elif (value != None):
            if (self.AB_choose > 0):
                if (value < self.est_speed):
                    self._speed = value
                else:
                    self._speed = self.est_speed
                    self.AB_choose = 0
                    print('here')
                # self._speed = min(value, self.est_speed)

            elif (self.AB_choose < 0):
                if (value > self.est_speed):
                    self._speed = value
                else:
                    self._speed = self.est_speed
                    self.AB_choose = 0
                # self._speed = max(value, self.est_speed)

            else:
                pass


    @property
    def est_speed(self):
        return self._est_speed

    @est_speed.setter
    def est_speed(self, value):
        if (value != None):
            if (value > self._est_speed):
                self.AB_choose = 1
                print('set')
            else:
                self.AB_choose = -1
            self._est_speed = min(value, SPEED_MAX)

    @property
    def accel(self):
        return self._accel

    @accel.setter
    def accel(self, value):
        if (value != None):
            self._accel = value

    @property
    def braking(self):
        return self._braking

    @braking.setter
    def braking(self, value):
        if (value != None):
            self._braking = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if (value != None):
            self._data = value


    def packageResolver(self):
        try:
            if (self.data != ''):
                start = self.data.find('255')
                end = self.data.find('254', start+3, len(self.data))

                if ((end != -1) and (start != -1)):
                    self.data = self.data[start+3:end]
                else:
                    return

                temp = self.data.split(' ')
                self.est_speed, self.accel, self.braking = float(temp[0]), float(temp[1]), float(temp[2])
                self.data = ''

        except ValueError:
            print('error')
        except IndexError:
            print('error')
        return


    def controller(self):
        dt = self.t - self.t_prev
        speed = self.speed
        est_speed = self.est_speed
        choose = self.AB_choose

        if (self.HARD_STOP == 0):
            if choose == 0:
                return dt * speed
            else:
                if (choose > 0):
                    accel = self.accel
                    speed_new = min(speed + self.accel * dt, est_speed)
                else:
                    accel = - self.braking
                    speed_new = max(speed - self.braking * dt, est_speed)

                l = (speed + speed_new) / 2 * dt
                self.speed = speed_new
                return l

                # accel = self.accel if (choose > 0) else -self.braking
                # if (choose > 0):
                #     print(accel)
                # speed_new = speed + accel * dt
                # speed_new = min(speed_new, est_speed) if (choose > 0) else max(speed_new, est_speed)
                # return l

        return 0


    def run(self):
        th = threading.currentThread()
        while getattr(th, "do_run", True):

            self.packageResolver()
            self.motor.dstep = self.controller()

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
        stringData = 't:\t{:.2f}\tangle:\t{:.2f}\tspeed:\t{:.2f}\taccel:\t{:.2f}\tbraking:\t{:.2f}\tch:\t{}\n'

        th = threading.currentThread()
        while getattr(th, "do_run", True):

            data = serial_recv(self.dev, 40)
            self.motor_control.data = data

            [x, y, z] = self.accel.getdata()

            thr = 2
            if (x > thr) or (z > thr):
                self.motor_control.speed = 0
                self.motor_control.est_speed = 0
                self.motor_control.HARD_STOP = 1
                print('got')
                print(x," ", y," ", z)

            #   FIXME:
            # Print message
            data = (self.motor_control.t, self.motor_control.motor.readAngle(),
                    self.motor_control.speed, self.motor_control.accel, self.motor_control.braking,
                    self.motor_control.AB_choose)
            self.writer.out = stringData.format(*data)
            # self.writer.out = '{}\n'.format(data)


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
