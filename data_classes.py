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

        self._acceleration = 0.0
        self._braking = 0.0
        self._velocity = 0.0

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
    velocity_signal = pyqtSignal(int)
    coordinate_signal = pyqtSignal(int)
    RSSI_signal = pyqtSignal(int)
    voltage_signal = pyqtSignal(int)
    current_signal = pyqtSignal(int)
    temperature_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self._velocity = 0.0
        self._coordinate = 0.0
        self._RSSI = 0.0
        self._voltage = 0.0
        self._current = 0.0
        self._temperature = 0.0

    @property  # Velocity value property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        if self._velocity != value:
            self._velocity = value
            self.velocity_signal.emit(value)

    @property  # Coordinate value property
    def coordinate(self):
        return self._coordinate

    @coordinate.setter
    def coordinate(self, value):
        if self._coordinate != value:
            self._coordinate = value
            self.coordinate_signal.emit(value)

    @property  # RSSI value property
    def RSSI(self):
        return self._RSSI

    @RSSI.setter
    def RSSI(self, value):
        if self._RSSI != value:
            self._RSSI = value
            self.RSSI_signal.emit(value)

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
        self.RSSI = package['RSSI']
        self.voltage = package['voltage']
        self.current = package['current']
        self.temperature = package['temperature']


#----------------------------------------------------------------------------------------------#
#   Keeps host's buttons data
class HBData(QObject):
    def __init__(self):
        super().__init__()
        self.base1 = 0.0
        self.base2 = 0.0
        self.left = 0
        self.right = 0
        self.soft_stop = 0
        self.end_points = 0
        self.end_points_behavior = 0
        self.sound_stop = 0
        self.swap_direction = 1
        self.accelerometer_stop = 0
        self.hard_stop = 0

        self.color_red = QColor(255, 0, 0).name()
        self.color_green = QColor(0, 255, 0).name()

    @staticmethod
    def set_color(button, color):
        button.setStyleSheet('QToolButton { background-color: %s}' % color)

    @pyqtSlot(bool)
    def enable_end_points(self, value):
        sender = self.sender()
        if value:
            color, self.end_points = self.color_green, 1
        else:
            color, self.end_points = self.color_red, 0
        self.set_color(sender, color)
