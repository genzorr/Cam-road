import struct, global_
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
        self.type = 1

        self._acceleration = 0.0
        self._braking = 0.0
        self._velocity = 0.0
        # FIXME: needed?
        self.mode = 0
        self.direction = 0
        self.set_base = 0

        self.crc = 0
        self.size = 4 * 7

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
    coordinate_signal = pyqtSignal(int)
    RSSI_signal = pyqtSignal(int)
    voltage_signal = pyqtSignal(int)
    current_signal = pyqtSignal(int)
    temperature_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.type = 2

        self.mode = 0
        self._coordinate = 0.0
        self._RSSI = 0.0
        self._voltage = 0.0
        self._current = 0.0
        self._temperature = 0.0
        self.base1 = 0.0
        self.base2 = 0.0

        self.crc = 0
        self.size = 4 * 9

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
        self.type = 3

        self.direction = 0
        self.soft_stop = False
        self.end_points = False
        self.end_points_stop = False
        self.end_points_reverse = False
        self.sound_stop = False
        self.swap_direction = False
        self.accelerometer_stop = False
        self.HARD_STOP = False
        self.lock_buttons = False

        self.crc = 0
        self.size = 4 * 2 + 9

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

#----------------------------------------------------------------------------------------------#

class PackageAnalyzer:
    def __init__(self):
        pass

    def encrypt_package(self, package):
        data = bytes()
        data += DESCR1
        data += DESCR2
        data += int_to_bytes(package.type)

        if package.type == 1:
            data += float_to_bytes(package.acceleration)
            data += float_to_bytes(package.braking)
            data += float_to_bytes(package.velocity)
            data += int_to_bytes(package.mode)
            data += int_to_bytes(package.direction)
            data += int_to_bytes(package.set_base)
            package.crc = package.acceleration + package.braking + package.velocity + \
                          package.mode + package.direction + package.set_base
            data += float_to_bytes(package.crc)

        elif package.type == 2:
            data += int_to_bytes(package.mode)
            data += float_to_bytes(package.coordinate)
            data += float_to_bytes(package.RSSI)
            data += float_to_bytes(package.voltage)
            data += float_to_bytes(package.current)
            data += float_to_bytes(package.temperature)
            data += float_to_bytes(package.base1)
            data += float_to_bytes(package.base2)
            package.crc = package.mode + package.coordinate + package.RSSI + \
                          package.voltage + package.current + package.temperature + \
                          package.base1 + package.base2
            data += float_to_bytes(package.crc)

        elif package.type == 3:
            data += int_to_bytes(package.direction)
            data += bool_to_bytes(package.soft_stop)
            data += bool_to_bytes(package.end_points)
            data += bool_to_bytes(package.end_points_stop)
            data += bool_to_bytes(package.end_points_reverse)
            data += bool_to_bytes(package.sound_stop)
            data += bool_to_bytes(package.swap_direction)
            data += bool_to_bytes(package.accelerometer_stop)
            data += bool_to_bytes(package.HARD_STOP)
            data += bool_to_bytes(package.lock_buttons)
            package.crc = package.direction + package.soft_stop + package.end_points + \
                          package.end_points_stop + package.end_points_reverse + package.sound_stop + \
                          package.swap_direction + package.accelerometer_stop + package.HARD_STOP + package.lock_buttons
            data += int_to_bytes(package.crc)

        else:
            return None

        return data

    def decrypt_package(self):
        try:
            while True:
                descr1 = global_.serial_device.read(1)
                descr2 = global_.serial_device.read(1)

                if descr1 != DESCR1 and descr2 != DESCR2:
                    if descr2 == DESCR1:
                        descr1 = DESCR1
                        descr2 = global_.serial_device.read(1)

                        if descr2 == DESCR2:
                            break

                    # print("Bad index", descr1, descr2)
                else: break

            crc = 0
            type = bytes_to_int(global_.serial_device.read(4))

            if type == 1:
                package = HTRData()
                package.type = 1

                data = global_.serial_device.read(package.size)
                if len(data) < package.size:
                    return None

                package.acceleration = bytes_to_float(data[0:4])
                package.braking = bytes_to_float(data[4:8])
                package.velocity = bytes_to_float(data[8:12])
                package.mode = bytes_to_int(data[12:16])
                package.direction = bytes_to_int(data[16:20])
                package.set_base = bytes_to_int(data[20:24])
                crc = package.acceleration + package.braking + package.velocity + \
                        package.mode + package.direction + package.set_base
                package.crc = bytes_to_float(data[24:28])
                if package.crc != crc:
                    print('Bad crc 1')
                    return None

            elif type == 2:
                package = RTHData()
                package.type = 2

                data = global_.serial_device.read(package.size)
                if len(data) < package.size:
                    return None

                package.mode = bytes_to_int(data[0:4])
                package.coordinate = bytes_to_float(data[4:8])
                package.RSSI = bytes_to_float(data[8:12])
                package.voltage = bytes_to_float(data[12:16])
                package.current = bytes_to_float(data[16:20])
                package.temperature = bytes_to_float(data[20:24])
                package.base1 = bytes_to_float(data[24:28])
                package.base2 = bytes_to_float(data[28:32])
                crc = package.mode + package.coordinate + package.RSSI + \
                      package.voltage + package.current + package.temperature + \
                      package.base1 + package.base2
                package.crc = bytes_to_float(data[32:36])
                if package.crc != crc:
                    print('Bad crc 2')
                    return None

            elif type == 3:
                package = HBData()
                package.type = 3

                data = global_.serial_device.read(package.size)
                if len(data) < package.size:
                    return None

                package.direction = bytes_to_int(data[0:4])
                package.soft_stop = bytes_to_bool(data[4:5])
                package.end_points = bytes_to_bool(data[5:6])
                package.end_points_stop = bytes_to_bool(data[6:7])
                package.end_points_reverse = bytes_to_bool(data[7:8])
                package.sound_stop = bytes_to_bool(data[8:9])
                package.swap_direction = bytes_to_bool(data[9:10])
                package.accelerometer_stop = bytes_to_bool(data[10:11])
                package.HARD_STOP = bytes_to_bool(data[11:12])
                package.lock_buttons = bytes_to_bool(data[12:13])
                crc = package.direction + package.soft_stop + package.end_points + \
                      package.end_points_stop + package.end_points_reverse + package.sound_stop + \
                      package.swap_direction + package.accelerometer_stop + package.HARD_STOP + package.lock_buttons
                package.crc = bytes_to_int(data[13:17])
                if package.crc != crc:
                    print('Bad crc 3')
                    return None
            else:
                print('error: no such package')
                return None

            return package

        except ValueError or IndexError:
            # print('error')
            return None
        except struct.error:
            # print(data)
            return None


def bool_to_bytes(c):
    b = struct.pack('=?', c)
    return b

def int_to_bytes(i):
    b = struct.pack('=i', i)
    return b

def float_to_bytes(f):
    b = struct.pack('=f', f)
    return b

def bytes_to_bool(b):
    (x,) = struct.unpack('=?', b)
    return x

def bytes_to_int(b):
    (x,) = struct.unpack('=i', b)
    return x

def bytes_to_float(b):
    (x,) = struct.unpack('=f', b)
    return x
