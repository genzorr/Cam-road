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


#----------------------------------------------------------------------------------------------#
#   Keeps 'road-to-host' data
class RTHData():
    def __init__(self):
        self.type = 2

        self.mode = 0
        self.coordinate = 0.0

        self.voltage = 0.0
        self.current = 0.0
        self.temperature = 0.0
        self.base1 = 0.0
        self.base2 = 0.0
        self.base1_set = False
        self.base2_set = False
        self.bases_init_swap = False

        self.direction = 0

#----------------------------------------------------------------------------------------------#
#   Keeps host's buttons data
class HBData():
    def __init__(self):
        self.type = 3

        self.soft_stop = False
        self.end_points_reset = False
        self.end_points = False
        self.end_points_stop = False
        self.end_points_reverse = False
        self.sound_stop = False
        self.swap_direction = False
        self.accelerometer_stop = False
        self.motor = False
        self.lock_buttons = False
        self.signal_behavior = 1

#----------------------------------------------------------------------------------------------#
class Mbee_data:
    def __init__(self):
        self.voltage = 0
        self.current = 0
        self.temperature = 0
