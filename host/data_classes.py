import struct
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor

DESCR1 = struct.pack('B', 0x7e)
DESCR2 = struct.pack('B', 0xa5)

#----------------------------------------------------------------------------------------------#
#   Keeps 'host-to-road' data
class HTRData(QObject):
    acceleration_signal = pyqtSignal(int)
    braking_signal = pyqtSignal(int)
    velocity_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.descr1 = DESCR1
        self.descr2 = DESCR2

        self._acceleration = 0.0
        self._braking = 0.0
        self._velocity = 0.0
        # FIXME: needed?
        self.mode = 0
        self.direction = 0
        self.set_base = 0
        self.crc = 0

        self.size = 7*4+2

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
        self.mode = 0
        self._coordinate = 0.0
        self._RSSI = 0.0
        self._voltage = 0.0
        self._current = 0.0
        self._temperature = 0.0
        self.base1 = 0.0
        self.base2 = 0.0


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

        self.color_red = QColor(255, 0, 0).name()
        self.color_green = QColor(0, 255, 0).name()

    @staticmethod
    def set_color(button, color):
        button.setStyleSheet('QToolButton { background-color: %s}' % color)

    @pyqtSlot(bool)
    def lock_buttons_(self, value):
        sender = self.sender()
        if value:
            color, self.lock_buttons = self.color_green, 1
        else:
            color, self.lock_buttons = self.color_red, 0
        self.set_color(sender, color)

    @pyqtSlot(bool)
    def enable_end_points_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.end_points = self.color_green, 1
            else:
                color, self.end_points = self.color_red, 0
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def end_points_stop_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.end_points_stop = self.color_green, 1
            else:
                color, self.end_points_stop = self.color_red, 0
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def end_points_reverse_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.end_points_reverse = self.color_green, 1
            else:
                color, self.end_points_reverse = self.color_red, 0
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def sound_stop_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.sound_stop = self.color_green, 1
            else:
                color, self.sound_stop = self.color_red, 0
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def swap_direction_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.swap_direction = self.color_green, 1
            else:
                color, self.swap_direction = self.color_red, 0
            self.set_color(sender, color)

    @pyqtSlot(bool)
    def stop_accelerometer_(self, value):
        if not self.lock_buttons:
            sender = self.sender()
            if value:
                color, self.accelerometer_stop = self.color_green, 1
            else:
                color, self.accelerometer_stop = self.color_red, 0
            self.set_color(sender, color)

#----------------------------------------------------------------------------------------------#

class PackageAnalyzer:
    def __init__(self, serial_device):
        self.dev = serial_device

    def encrypt_package(self, package):
        data = bytes()
        data += package.descr1
        data += package.descr2
        data += float_to_bytes(package.acceleration)
        data += float_to_bytes(package.braking)
        data += float_to_bytes(package.velocity)
        data += int_to_bytes(package.mode)
        data += int_to_bytes(package.direction)
        data += int_to_bytes(package.set_base)
        # for i in range(2, package.size - 4):
        #     package.crc += int(data[i])
        crc = int(0)
        data += int_to_bytes(package.crc)
        # print('{}\t{}'.format(data, len(data)))
        return data

    def decrypt_package(self):
        packet = HTRData()
        try:
            while True:
                packet.descr1 = self.dev.read(1)
                packet.descr2 = self.dev.read(1)

                if packet.descr1 != DESCR1 and packet.descr2 != DESCR2:
                    if packet.descr2 == DESCR1:
                        packet.descr1 = DESCR1
                        packet.descr2 = self.dev.read(1)

                        if packet.descr2 == DESCR2:
                            break

                    print("Bad index", packet.descr1, packet.descr2)
                else: break

            crc = 0
            data = self.dev.read(packet.size)
            for i in range(0, packet.size-2-4):
                crc += data[i]

            packet.crc = data[24:28]
            if packet.crc != crc:
                print('Bad crc')
                return None

            packet.acceleration = bytes_to_float(data[0:4])
            packet.braking = bytes_to_float(data[4:8])
            packet.velocity = bytes_to_float(data[8:12])
            packet.mode = bytes_to_int(data[12:16])
            packet.direction = bytes_to_int(data[16:20])
            packet.set_base = bytes_to_int(data[20:24])

        except ValueError or IndexError:
            print('error')
            return None
        return packet


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
