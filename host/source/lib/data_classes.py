import global_
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor

#----------------------------------------------------------------------------------------------#
#   Keeps 'host-to-road' data
class HTRData(QObject):
    acceleration_signal = pyqtSignal(int)
    braking_signal = pyqtSignal(int)
    velocity_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.type = 1

        self._acceleration = 0.0
        self._braking = 0.0
        self._velocity = 0.0
        self.mode = 0
        self.direction = 1
        self.set_base = 0


    @property  # Acceleration value property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        if self._acceleration != value:
            self._acceleration = value
            self.acceleration_signal.emit(value)

    @property  # Braking value property
    def braking(self):
        return self._braking

    @braking.setter
    def braking(self, value):
        if self._braking != value:
            self._braking = value
            self.braking_signal.emit(value)

    @property  # Velocity value property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        if self._velocity != value:
            self._velocity = value
            self.velocity_signal.emit(value)

    # Updates data from encoders
    @pyqtSlot()
    def dataUpdate(self, package):
        self.acceleration = package['acceleration']
        self.braking = package['braking']
        self.velocity = package['velocity']


#----------------------------------------------------------------------------------------------#
#   Keeps 'road-to-host' data
class RTHData(QObject):
    coordinate_signal = pyqtSignal(float)
    voltage_signal = pyqtSignal(float)
    current_signal = pyqtSignal(float)
    temperature_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.type = 2

        self.mode = 0
        self._coordinate = 0.0

        self._voltage = 0.0
        self._current = 0.0
        self._temperature = 0.0
        self.base1 = 0.0
        self.base2 = 0.0
        self.base1_set = False
        self.base2_set = False

        self.direction = 0

    @property  # Coordinate value property
    def coordinate(self):
        return self._coordinate

    @coordinate.setter
    def coordinate(self, value):
        if self._coordinate != value:
            self._coordinate = value
            self.coordinate_signal.emit(value)

    @property  # Voltage value property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        if self._voltage != value:
            self._voltage = value
            self.voltage_signal.emit(value)

    @property  # Current value property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        if self._current != value:
            self._current = value
            self.current_signal.emit(value)

    @property  # Temperature value property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if self._temperature != value:
            self._temperature = value
            self.temperature_signal.emit(value)

    # Updates data from gotten MBee package
    @pyqtSlot()
    def dataUpdate(self, package):
        self.velocity = package['velocity']
        self.coordinate = package['coordinate']
        self.voltage = package['voltage']
        self.current = package['current']
        self.temperature = package['temperature']


#----------------------------------------------------------------------------------------------#
#   Keeps host's buttons data
class HBData(QObject):
    def __init__(self):
        super().__init__()
        self.type = 3

        self.soft_stop = False
        self.end_points_reset = False
        self.end_points = False
        self.end_points_stop = False
        self.end_points_reverse = False
        self.sound_stop = False
        self.swap_direction = False
        self.accelerometer_stop = False
        self.HARD_STOP = False
        self.lock_buttons = False

        self.color_red = QColor(255, 0, 0).name()
        self.color_green = QColor(0, 255, 0).name()

    @staticmethod
    def set_color(button, color):
        button.setStyleSheet('QToolButton { background-color: %s}' % color)

    @pyqtSlot(bool)
    def lock_buttons_(self, value):
        sender = self.sender()
        if value:
            color, self.lock_buttons = self.color_green, True
        else:
            color, self.lock_buttons = self.color_red, False
        self.set_color(sender, color)

    @pyqtSlot(bool)
    def enable_end_points_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.end_points = self.color_green, True
            else:
                color, self.end_points = self.color_red, False
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def end_points_stop_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.end_points_stop = self.color_green, True
            else:
                color, self.end_points_stop = self.color_red, False
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def end_points_reverse_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.end_points_reverse = self.color_green, True
            else:
                color, self.end_points_reverse = self.color_red, False
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def sound_stop_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.sound_stop = self.color_green, True
            else:
                color, self.sound_stop = self.color_red, False
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def swap_direction_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.swap_direction = self.color_green, True
            else:
                color, self.swap_direction = self.color_red, False
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def stop_accelerometer_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.accelerometer_stop = self.color_green, True
            else:
                color, self.accelerometer_stop = self.color_red, False
            self.set_color(sender, color)
