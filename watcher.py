import serial
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject

ACCUM_LEN = 1

#----------------------------------------------------------------------------------------------#
#   Keeps 'external' data
class ExternalData(QObject):
    acceleration_signal = pyqtSignal(int)
    braking_signal = pyqtSignal(int)
    velocity_signal = pyqtSignal(int)
    coordinate_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._acceleration = 0.0
        self._braking = 0.0
        self._velocity = 0.0
        self._coordinate = 0.0

    @property  # Acceleration value property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        self._acceleration = value

    @property  # Braking value property
    def braking(self):
        return self._braking

    @braking.setter
    def braking(self, value):
        self._braking = value

    @property  # Velocity value property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self._velocity = value

    @property  # Coordinate value property
    def coordinate(self):
        return self._coordinate

    @coordinate.setter
    def coordinate(self, value):
        self._coordinate = value


#----------------------------------------------------------------------------------------------#
#   Stores messages
class MsgAccumulator:
    def __init__(self, batch_size, signal):
        self.batch_size = batch_size
        self.signal = signal
        self.accumulator = []

    def push_message(self, msg):
        self.accumulator.append(msg)
        if len(self.accumulator) >= self.batch_size:
            self.signal.emit(self.accumulator)
            self.accumulator = []


#----------------------------------------------------------------------------------------------#
#   Main thread for getting / throwing data from/to MBee module and checking it for all's OK
class WatcherThread(QThread):
    def __init__(self, speed=9600, port='/dev/ttyUSB0', window=None):
        QThread.__init__(self)
        self.device = serial_init(speed, port)

        self.externalData = ExternalData()
        # self.internalData = InternalData()

        #   Signals to slots connection
        if window.workWidget:
            self.externalData.acceleration_signal.connect(window.workWidget.ui.Acceleration.setValue)
            self.externalData.braking_signal.connect(window.workWidget.ui.Braking.setValue)
            self.externalData.velocity_signal.connect(window.workWidget.ui.Velocity.setValue)
            self.externalData.coordinate_signal.connect(window.workWidget.ui.Coordinate.setTickPosition)


    def run(self):
        while True and self.device:
            data = serial_recv(self.device)

            if data:
                data = int(data)
                # TODO: getting data from packages (bytes or smth else)

#----------------------------------------------------------------------------------------------#

def serial_init(speed, port):
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

def serial_recv(dev):
    string = dev.read(255).decode()
    return string

def serial_send(dev, string):
    dev.write(string.encode('utf-8'))