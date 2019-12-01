import time, global_
import sys
sys.path.append('../../fortune-controls/Lib')
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from x4motor import X4Motor

from queue import LifoQueue

# sudo ./modbus -r -d /dev/ttySAC3 -b 115200 -f 3 -s 2 -a 0 -n 20
#----------------------------------------------------------------------------------------------#
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
STOP = 0
COURSE = 1
COURSE_BASES = 2
EMERGENCY = 5


class FSM:
    def __init__(self, init_state):
        self.stack = LifoQueue()

    def update(self):
        currentStateFunction = self.getCurrentState()
        if currentStateFunction is not None:
            currentStateFunction()

    def popState(self):
        self.stack.get_nowait()

    def pushState(self, state):
        if (self.getCurrentState() != state):
            self.stack.put(state)

    def changeState(state):
        with global_.lock:
            self.stack.get_nowait()
            if (self.getCurrentState() != state):
                self.stack.put(state)


    def getCurrentState(self):
        lenght = self.stack.qsize()
        return self.stack[length - 1] if (lenght > 0) else None


class Controller(FSM):
    def __init__(self):
        super(FSM, self).__init__(self.stop)
        try:
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
        # else:
        #     self.motor = None

        self.starttime = time.time()

        self.t = 0.0
        self.t_prev = 0.0

        self._speed = 0.0
        self._accel = 0.0
        self._braking = 0.0
        self.AB_choose = 0
        self._est_speed = 0.0
        self._HARD_STOP = 0
        self.SOFT_STOP = 0

        self.dstep = 0
        self.coordinate = 0

        self.direction_changed = 0


        self.mode = 0
        self.direction = 0
        self.change_direction = 0
        self.is_braking = 0

        self._base1 = 0.0
        self._base2 = 0.0
        self.base1_set = False
        self.base2_set = False


    def off(self):
        try:
            self.motor.release()    # Release motor
            self.client.close()

    #---------- PROPERTIES ----------#
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
        self._base1 = value
        self.base1_set = True

    @property
    def base2(self):
        return self._base2

    @base2.setter
    def base2(self, value):
        self._base2 = value
        if (value < self._base1):
            self._base2 = self._base1
            self._base1 = value
        self.base2_set = True
    #--------------------------------#

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


    def stop(self):
        if self.direction != 0:
            self.HARD_STOP = 0
            self.SOFT_STOP = 0
            self.changeState(self.course)

        self.dstep = self.calc_dstep(speed_to=0)
        self.coordinate += self.dstep
            # if (self.base1_set and self.base2_set):
            #     self.stack.pushState(self.course_bases)
            # else:
            #     self.stack.pushState(self.course)

    def stop_transitial(self):
        if (self.HARD_STOP or self.SOFT_STOP):
            self.changeState(self.stop)

        if (self.speed == 0):
            self.direction = - self.direction
            self.changeState(self.course)

        self.dstep = self.calc_dstep(speed_to=0)
        self.coordinate += self.dstep


    def course(self):
        if (self.HARD_STOP or self.SOFT_STOP):
            self.changeState(self.stop)

        if (self.base1_set and self.base2_set):
            if self.direction == -1:
                dist_to_base = coord - self.base1
            else:
                dist_to_base = self.base2 - coord

            braking_dist = speed * speed / (2 * braking) if braking != 0 else 0
            if dist_to_base <= braking_dist:
                self.changeState(self.stop_transitial)
        else:
            self.dstep = self.calc_dstep(speed_to=self.est_speed)

        self.coordinate += self.dstep


    """ Returns motor dstep value """
    def control(self):
        speed = self.speed
        coord = self.coordinate
        braking = self.braking

        # out_of_breaking = True

        # Update time
        self.t_prev = self.t
        self.t = time.time() - self.starttime

        if self.HARD_STOP == 1:
            pass
        elif self.mode == STOP and self.speed == 0:
            pass
        else:
            if self.mode == STOP:
                dstep = self.calc_dstep(speed_to=0)

                if self.is_braking and (self.speed == 0):
                    self.direction = - self.direction
                    self.is_braking = 0
                    self.mode = COURSING

            elif self.mode == COURSING:
                #   In this mode road will be coursing between two bases

                #   Consider braking into bases points
                if self.base1_set and self.base2_set:
                    distance = self.base2 - self.base1

                    if not self.was_in_zone and ((self.coordinate < self.base1) or (self.coordinate > self.base2)):
                        dstep = self.calc_dstep(speed_to=self.est_speed)
                    else:
                        self.was_in_zone = True

                        if self.direction == -1:
                            dist_to_base = coord - self.base1
                        else:
                            dist_to_base = self.base2 - coord

                        if not self.is_braking:
                            braking_dist = speed * speed / (2 * braking) if braking != 0 else 0
                            if dist_to_base <= braking_dist:
                                self.is_braking = 1
                                self.est_speed = 0
                                self.mode = 0
                                dstep = self.calc_dstep(speed_to=0)

                                # # FIXME: seems strange, I should change direction when JUST stopped
                                # if out_of_breaking and (dist_to_base < abs(dstep)):
                                #     out_of_breaking = False
                                #     dstep = dist_to_base * self.direction
                                #     self.direction = -self.direction
                                #     self.change_direction = 1 if self.change_direction == 0 else 0
                                # else:
                                #     dstep = 0
                            else:
                                self.is_braking = 0
                                dstep = self.calc_dstep(speed_to=self.est_speed)
                        else:
                            dstep = 0
                else:
                    dstep = self.calc_dstep(speed_to=self.est_speed)

            else:
                dstep = 0

            self.coordinate += dstep
            return dstep
        return 0
