import time, serial
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

            # FIXME: REMOVE
            window.workWidget.ui.Velocity.valueChanged.connect(self.veloChange)

        if window.settingsWidget:
            window.settingsWidget.ui.EnableEndPoints.toggled.connect(self.outerData.enable_end_points_)
            window.settingsWidget.ui.EndPointsStop.toggled.connect(self.outerData.end_points_stop_)
            window.settingsWidget.ui.EndPointsReverse.toggled.connect(self.outerData.end_points_reverse_)
            window.settingsWidget.ui.SoundStop.toggled.connect(self.outerData.sound_stop_)
            window.settingsWidget.ui.SwapDirection.toggled.connect(self.outerData.swap_direction_)
            window.settingsWidget.ui.StopAccelerometer.toggled.connect(self.outerData.stop_accelerometer_)
            window.settingsWidget.ui.LockButtons.toggled.connect(self.outerData.lock_buttons_)

            '''Stop-reverse end points behavior'''
            window.settingsWidget.ui.EndPointsStop.pressed.connect(window.settingsWidget.setChecked)
            window.settingsWidget.ui.EndPointsReverse.pressed.connect(window.settingsWidget.setChecked)

            window.settingsWidget.ui.EnableEndPoints.toggled.emit(False)
            window.settingsWidget.ui.EndPointsStop.toggled.emit(False)
            window.settingsWidget.ui.EndPointsReverse.toggled.emit(False)
            window.settingsWidget.ui.SoundStop.toggled.emit(False)
            window.settingsWidget.ui.SwapDirection.toggled.emit(False)
            window.settingsWidget.ui.StopAccelerometer.toggled.emit(False)
            window.settingsWidget.ui.LockButtons.toggled.emit(False)

    # FIXME: REMOVE
    def veloChange(self, value):
        self.hostData.velocity = value
        # self.hostData.acceleration = 1
        # self.hostData.braking = 1


    def run(self):
        VELO_MAX = 15
        while True and self.device:
            # data = serial_recv(self.device)
            accel = 1
            braking = 1
            data = str(0xFF)+str(self.hostData.velocity * VELO_MAX / 100)+' '+str(accel)+' '+str(braking)+str(0xFE)
            serial_send(self.device, data)
            # print(self.hostData.velocity)
            # time.sleep(0.5)

            # if data:
            #     data = int(data)
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