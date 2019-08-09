import serial
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from data_classes import *

ACCUM_LEN = 1


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
#   Main thread for getting / throwing data from/to MBee module and for checking all's OK
class WatcherThread(QThread):
    def __init__(self, speed=9600, port='/dev/ttyUSB0', window=None):
        QThread.__init__(self)
        self.device = serial_init(speed, port)

        self.hostData = HTRData()
        self.roadData = RTHData()
        self.outerData = HBData()

        #   Signals to slots connection
        if window.workWidget:
            self.hostData.acceleration_signal.connect(window.workWidget.ui.Acceleration.setValue)
            self.hostData.braking_signal.connect(window.workWidget.ui.Braking.setValue)
            # TODO: ACKNOWLEDGE
            self.hostData.velocity_signal.connect(window.workWidget.ui.Velocity.setValue)
            self.roadData.coordinate_signal.connect(window.workWidget.ui.Coordinate.setValue)

        if window.settingsWidget:
            window.settingsWidget.ui.EndPointsEnable.toggled.connect(self.outerData.enable_end_points)
            # self.ui.EndPointsBehavior.toggled.connect(self.button_toggled)
            # self.ui.SoundStop.toggled.connect(self.button_toggled)
            # self.ui.SwapDirection.toggled.connect(self.button_toggled)
            # self.ui.StopAccelerometer.toggled.connect(self.button_toggled)
            #
            window.settingsWidget.ui.EndPointsEnable.toggled.emit(False)
            # self.ui.EndPointsBehavior.toggled.emit(False)
            # self.ui.SoundStop.toggled.emit(False)
            # self.ui.SwapDirection.toggled.emit(False)
            # self.ui.StopAccelerometer.toggled.emit(False)

    def run(self):
        while True and self.device:
            data = serial_recv(self.device)

            # if data:
            #     data = int(data)
            # TODO: getting data from packages (bytes or smth else)
        while True:
            i = 0

#----------------------------------------------------------------------------------------------#

def serial_init(speed, port):
    try:
        dev = serial.Serial(
        port=port,
        baudrate=speed,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1 )
    except serial.serialutil.SerialException:
        print('Could not open port')
        dev = None

    return dev

def serial_recv(dev):
    string = dev.read(255).decode()
    return string

def serial_send(dev, string):
    dev.write(string.encode('utf-8'))