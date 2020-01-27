import time
import sys
sys.path.append('../../../fortune-controls/Lib')

import global_
from global_ import get_logger
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from x4motor import X4Motor

# sudo ./modbus -r -d /dev/ttySAC3 -b 115200 -f 3 -s 2 -a 0 -n 20
#----------------------------------------------------------------------------------------------#
#   Settings
config = {'id': 1,\
        'Mode': 'Angle',\
        'PWM_Limit' : 900,\
        'PWM_inc_limit' : 2,\
        'I_limit': 5.0,\
        'V_min': 12.0,\
        'Angle_PID_P' : 50,\
        'Angle_PID_I' : 1,\
        'Speed_PID_P' : 100,\
        'Speed_PID_I' : 100,\
        'StepsPerMM': 210,\
        'TimeOut' : 1000,\
        'TempShutDown' : 100,\
        'Reverse': 0}           #   210 - 1step = 0.01m

#----------------------------------------------------------------------------------------------#
STOP = 0
REVERSE = 1


class FSM:
    def __init__(self, init_state):
        self.stack = []
        self.stack.append(init_state)
        self.len = 1

    def update(self):
        currentStateFunction = self.getCurrentState()
        if currentStateFunction is not None:
            currentStateFunction()

    def popState(self):
        self.stack.pop()
        self.len -= 1

    def pushState(self, state):
        if self.getCurrentState() != state:
            self.stack.put(state)
            self.len += 1

    def changeState(self, state):
        global_.lock.acquire(blocking=True, timeout=1)
        self.stack.pop()
        self.len -= 1
        if (self.len == 0) or (self.getCurrentState() != state):
            self.stack.append(state)
            self.len += 1
        global_.lock.release()

    def getCurrentState(self):
        global_.lock.acquire(blocking=True, timeout=1)
        state = self.stack[self.len - 1]
        global_.lock.release()

        return state


class Controller(FSM):
    def __init__(self):
        super().__init__(self.stop)
        self.logger = get_logger('Control')

        try:
            self.client = ModbusClient(method = "rtu", port="/dev/ttyS1", stopbits = 1,
                                       bytesize = 8, parity = 'N', baudrate= 115200,
                                       timeout = 0.8, strict=False )

            #   Try to connect to modbus client
            client_status = self.client.connect()
            if client_status:
                self.logger.info('# Controller OK')
            else:
                self.logger.warning('# Controller is not initialized')
                self.motor = None
                self.client = None

            #   Motor initialization
            self.motor = X4Motor(self.client, settings=config)
            if self.motor:
                self.logger.info('# Motor OK')
            else:
                self.logger.warning('# Motor is not initialized')
                self.motor = None
                self.client = None

            #   Print all registers
            # registers = self.motor.readAllRO()
            # print(registers)

        except BaseException:
            self.motor = None

        self.starttime = time.time()

        self.t = 0.0
        self.t_prev = 0.0

        self._speed = 0.0
        self._accel = 0.0
        self._braking = 0.0
        self.AB_choose = 0
        self._est_speed = 0.0
        self._HARD_STOP = 0
        self.soft_stop = 0
        self.reverse = 0
        self.stopped = 0
        self.continue_ = 0

        self.end_points = True
        self.end_points_stop = True
        self.end_points_reverse = False

        self.dstep = 0
        self.coordinate = 0

        self.mode = 0
        self.direction = 0

        self._base1 = 0.0
        self._base2 = 0.0
        self.base1_set = False
        self.base2_set = False


    def off(self):
        if self.motor:
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
            else:
                self.AB_choose = 0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value is not None:
            if self.AB_choose > 0:
                # if value < self.est_speed:
                #     self._speed = value
                # else:
                #     self._speed = self.est_speed
                #     self.AB_choose = 0
                self._speed = min(value, self.est_speed)

            elif self.AB_choose < 0:
                # if value > self.est_speed:
                #     self._speed = value
                # else:
                #     self._speed = self.est_speed
                #     self.AB_choose = 0
                self._speed = max(value, self.est_speed)

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
        return (self.t, self.speed, self.est_speed, self.base1, self.base2, self.mode, self.coordinate, tmp, self.HARD_STOP)

    def update_coordinate(self, speed_to):
        dt = self.t - self.t_prev
        if self.AB_choose == 0:
            speed_new = self.speed
        elif self.AB_choose > 0:
            speed_new = min(self.speed + self.accel * dt, speed_to)
        else:
            speed_new = max(self.speed - self.braking * dt, speed_to)

        self.dstep = (self.speed + speed_new) / 2 * dt * self.direction
        self.speed = speed_new
        self.coordinate += self.dstep


    def stop(self):
        self.mode = 0
        self.est_speed = 0

        if self.HARD_STOP:
            self.dstep = 0

        if (self.speed == 0) and not self.stopped:
            self.direction = 0
            self.stopped = 1

        self.update_coordinate(speed_to=0)

        #  Exit from state.
        if ((self.stopped) and (self.direction != 0)):
            self.HARD_STOP = 0                              # CHANGED
            self.stopped = 0
            self.soft_stop = 0
            self.changeState(self.course)

    def stop_transitial(self):
        self.mode = 1
        self.est_speed = 0

        self.update_coordinate(speed_to=0)

        #  Exit from state.
        if (self.HARD_STOP or self.soft_stop):
            self.reverse = 0
            self.changeState(self.stop)

        if self.continue_ == 1:
            self.reverse = 0
            self.continue_ = 0
            self.changeState(self.course)

        if (self.speed == 0.0):
            self.direction = - self.direction
            self.reverse = 0
            self.changeState(self.course)


    def course(self):
        self.mode = 2
        self.est_speed = global_.hostData.velocity * global_.VELO_MAX / 100

        #  Bases are set.
        if self.end_points and (self.base1_set and self.base2_set):
            #  Check here that we are in base area and go here if not.
            out_left = True if (self.coordinate <= self.base1) else False
            out_right = True if (self.coordinate >= self.base2) else False

            if out_left:    # We are to the left of the 1st base.
                if (self.direction == -1):
                    self.reverse = 1
                    self.changeState(self.stop_transitial)
                    return

                dist_to_base = self.base1 - self.coordinate
                braking_dist = self.speed * self.speed / (2 * self.braking) if self.braking != 0 else 0

                if self.end_points_stop and (dist_to_base <= braking_dist-1):
                    self.changeState(self.stop)
                    return

                #  Direction = +1
                self.update_coordinate(speed_to=self.est_speed)

            elif out_right: # We are to the right of the 2nd base.
                if (self.direction == 1):
                    self.reverse = 1
                    self.changeState(self.stop_transitial)
                    return

                dist_to_base = self.coordinate - self.base2
                braking_dist = self.speed * self.speed / (2 * self.braking) if self.braking != 0 else 0

                if self.end_points_stop and (dist_to_base <= braking_dist-1):
                    self.changeState(self.stop)
                    return

                #  Direction = -1
                self.update_coordinate(speed_to=self.est_speed)

            elif (not out_left) and (not out_right):    # We are in area
                if self.direction == -1:
                    dist_to_base = self.coordinate - self.base1
                else:
                    dist_to_base = self.base2 - self.coordinate

                #  Consider if we should break before going to base point.
                braking_dist = self.speed * self.speed / (2 * self.braking) if self.braking != 0 else 0

                if (dist_to_base <= braking_dist+1):
                    if self.end_points_stop:
                        self.changeState(self.stop)
                    elif self.end_points_reverse:
                        self.changeState(self.stop_transitial)
                    return

                #  Update speed as usual if we do not need to break.
                self.update_coordinate(speed_to=self.est_speed)

        #  Bases are not set.
        else:
            self.update_coordinate(speed_to=self.est_speed)

        #  Exit from state.
        if (self.HARD_STOP or self.soft_stop):
            self.changeState(self.stop)

        if self.reverse:
            self.changeState(self.stop_transitial)
