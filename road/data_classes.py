import time

#----------------------------------------------------------------------------------------------#
#   Keeps 'host-to-road' data
class HTRData():
    def __init__(self):
        self.acceleration = 0.0
        self.braking = 0.0
        self.velocity = 0.0

        # FIXME: needed?
        self.mode = 0
        self.direction = 0
        self.set_base = 0


#----------------------------------------------------------------------------------------------#
#   Keeps 'road-to-host' data
class RTHData():
    def __init__(self):
        self.mode = 0
        self.coordinate = 0.0
        self.RSSI = 0.0
        self.voltage = 0.0
        self.current = 0.0
        self.temperature = 0.0
        self.base1 = 0.0
        self.base2 = 0.0

#----------------------------------------------------------------------------------------------#
#   Keeps host's buttons data
class HBData():
    def __init__(self):
        self.left = 0
        self.right = 0
        self.soft_stop = 0
        self.end_points = 0
        self.end_points_stop = 0
        self.end_points_reverse = 0
        self.sound_stop = 0
        self.swap_direction = 0
        self.accelerometer_stop = 0
        self.HARD_STOP = 0
        self.lock_buttons = 0

#----------------------------------------------------------------------------------------------#
SPEED_MAX = 20

STOP = 0
COURSING = 1
BUTTONS = 2

class Controller:
    def __init__(self, motor, classes):
        self.motor = motor
        self.hostData = classes[0]
        self.roadData = classes[1]
        self.specialData = classes[2]

        self.data = ''
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

    def get_data(self):
        # Print message
        if self.direction == 1:
            tmp = "+"
        elif self.direction == -1:
            tmp = "-"
        else:
            tmp = " "
        return [self.t, self.speed, self.base1, self.base2,
                self.mode, self.coordinate, tmp]

#    """
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

        except ValueError or IndexError:
            print('error')
        return
#    """

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
                pass

            self.coordinate += dstep
            # FIXME: return
            # self.motor.dstep = dstep


