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
        self.direction = 0
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
        self.bases_init_swap = False

        self.direction = -1

    def __eq__(self, other):
        return isinstance(other, type(self)) and (self.__dict__ == other.__dict__)

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
        self.motor = False
        self.lock_buttons = False
        self.signal_behavior = 1

        self.color_red = QColor(255, 0, 0).name()
        self.color_green = QColor(0, 255, 0).name()
        self.color_orange = QColor(255, 165, 0).name()

        self.slots = [  self.enable_end_points_, self.end_points_stop_, self.end_points_reverse_,\
                        self.sound_stop_, self.swap_direction_, self.stop_accelerometer_]
        self.last_states = []

    def __eq__(self, other):
        return isinstance(other, type(self)) and (self.__dict__ == other.__dict__)

    @staticmethod
    def color_button(button, color):
        button.setStyleSheet('QToolButton { background-color: %s}' % color)

    def set_color(self, button, state):
        color = self.color_green if (state is True) else self.color_red
        button.setStyleSheet('QToolButton { background-color: %s}' % color)

    def save_state(self, state):
        self.sender().setChecked(not state)

    @pyqtSlot(bool)
    def lock_buttons_(self, value):
        self.lock_buttons = value
        self.set_color(self.sender(), value)

        if value:
            self.last_states = []
            global_.window.settingsWidget.ui.EndPointsReverse.setAutoExclusive(False)
            global_.window.settingsWidget.ui.EndPointsStop.setAutoExclusive(False)
            for button in global_.window.settingsWidget.buttons:
                self.last_states.append(button.isChecked())
                button.setChecked(False)
                button.setCheckable(False)

        else:
            global_.window.settingsWidget.ui.EndPointsReverse.setAutoExclusive(True)
            global_.window.settingsWidget.ui.EndPointsStop.setAutoExclusive(True)
            for (button, state) in zip(global_.window.settingsWidget.buttons, self.last_states):
                button.setCheckable(True)
                button.setChecked(state)

    @pyqtSlot(bool)
    def enable_end_points_(self, value):
        if not self.lock_buttons:
            self.end_points = value
            self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def end_points_stop_(self, value):
        if not self.lock_buttons:
            self.end_points_stop = value
            self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def end_points_reverse_(self, value):
        if not self.lock_buttons:
            self.end_points_reverse = value
            self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def sound_stop_(self, value):
        if not self.lock_buttons:
            self.sound_stop = value
            self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def swap_direction_(self, value):
        if not self.lock_buttons:
            self.swap_direction = value
            self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def stop_accelerometer_(self, value):
        if not self.lock_buttons:
            self.accelerometer_stop = value
            self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def sig_stop_(self, value):
        if value:
            self.signal_behavior = 1
        self.set_color(self.sender(), value)
        
    @pyqtSlot(bool)
    def sig_ret1_(self, value):
        if value:
            self.signal_behavior = 2
        self.set_color(self.sender(), value)

    @pyqtSlot(bool)
    def sig_ret2_(self, value):
        if value:
            self.signal_behavior = 3
        self.set_color(self.sender(), value)


    @pyqtSlot(bool)
    def base1_(self, value):
        if value:
            if self.enable_end_points_:
                color = self.color_green
            else:
                color = self.color_orange
        else:
            color = self.color_red
        self.color_button(global_.window.workWidget.ui.Base1, color)

        # Show base numbers.
        if global_.roadData.bases_init_swap:
            global_.window.workWidget.ui.Base1.setText('2')
            global_.window.workWidget.ui.Base2.setText('1')
        else:
            global_.window.workWidget.ui.Base1.setText('1')
            global_.window.workWidget.ui.Base2.setText('2')

    @pyqtSlot(bool)
    def base2_(self, value):
        if value:
            if self.enable_end_points_:
                color = self.color_green
            else:
                color = self.color_orange
        else:
            color = self.color_red
        self.color_button(global_.window.workWidget.ui.Base2, color)

        # Show base numbers.
        if global_.roadData.bases_init_swap:
            global_.window.workWidget.ui.Base1.setText('2')
            global_.window.workWidget.ui.Base2.setText('1')
        else:
            global_.window.workWidget.ui.Base1.setText('1')
            global_.window.workWidget.ui.Base2.setText('2')
