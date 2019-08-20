import time, serial, global_
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from data_classes import *
from mbee import serialstar


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

class MbeeThread_write(QThread):
    def __init__(self, serial_device):
        QThread.__init__(self)
        self.alive = 0
        # self.mbee = serialstar.SerialStar(port, speed)
        self.mbee = serial_device
        self.analyzer = PackageAnalyzer(self.mbee)

    def run(self):
        while True and self.mbee:
            global_.hostData.acceleration = 3
            global_.hostData.braking = 3

            # Transmitting
            # if not global_.serial_lock:
            #     global_.serial_lock = 1
            #     data = self.analyzer.encrypt_package(global_.hostData)
            #     self.mbee.write(data)
            #     data = self.analyzer.encrypt_package(global_.specialData)
            #     self.mbee.write(data)
            #     global_.serial_lock = 0

            data = self.analyzer.encrypt_package(global_.hostData)
            self.mbee.write(data)
            data = self.analyzer.encrypt_package(global_.specialData)
            self.mbee.write(data)

    #   Callback functions for SerialStar
    # def frame_81_received(packet):
    #     print("Received 81-frame.")
    #     print(packet)

class MbeeThread_read(QThread):
    def __init__(self, serial_device):
        QThread.__init__(self)
        self.alive = 0
        # self.mbee = serialstar.SerialStar(port, speed)
        self.mbee = serial_device
        self.analyzer = PackageAnalyzer(self.mbee)

    def run(self):
        while True and self.mbee:
            # Receiving
            # if not global_.serial_lock:
            #     global_.serial_lock = 1
            #     package = self.analyzer.decrypt_package()
            #     global_.serial_lock = 1
            package = self.analyzer.decrypt_package()

            if isinstance(package, RTHData):
                print('got')
                global_.roadData = package

#----------------------------------------------------------------------------------------------#
#   Main thread for getting / throwing data from/to MBee module and for checking all's OK
class WatcherThread(QThread):
    def __init__(self, window=None):
        QThread.__init__(self)

        #   Signals to slots connection
        if window.workWidget:
            global_.hostData.acceleration_signal.connect(window.workWidget.ui.Acceleration.setValue)
            global_.hostData.braking_signal.connect(window.workWidget.ui.Braking.setValue)
            global_.hostData.velocity_signal.connect(window.workWidget.ui.Velocity.setValue)
            global_.roadData.coordinate_signal.connect(window.workWidget.ui.Coordinate.setValue)

            # FIXME: REMOVE
            window.workWidget.ui.Velocity.valueChanged.connect(self.veloChange)

        if window.settingsWidget:
            window.settingsWidget.ui.EnableEndPoints.toggled.connect(global_.specialData.enable_end_points_)
            window.settingsWidget.ui.EndPointsStop.toggled.connect(global_.specialData.end_points_stop_)
            window.settingsWidget.ui.EndPointsReverse.toggled.connect(global_.specialData.end_points_reverse_)
            window.settingsWidget.ui.SoundStop.toggled.connect(global_.specialData.sound_stop_)
            window.settingsWidget.ui.SwapDirection.toggled.connect(global_.specialData.swap_direction_)
            window.settingsWidget.ui.StopAccelerometer.toggled.connect(global_.specialData.stop_accelerometer_)
            window.settingsWidget.ui.LockButtons.toggled.connect(global_.specialData.lock_buttons_)

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
        global_.hostData.velocity = value


    def run(self):
        # VELO_MAX = 30
        # while True and self.device:
            # accel = 3
            # braking = 3
            # data = str(0xFF)+\
            #        str(self.hostData.velocity * VELO_MAX / 100)+\
            #        ' '+str(accel)+' '+str(braking)+' '+\
            #        str(self.control.mode)+' '+\
            #        str(self.control.direction)+' '+\
            #        str(self.control.set_base)+\
            #        str(0xFE)
            # serial_send(self.device, data)
        while True:
            if time.time() % 2 == 0:
                print('{}\t{}'.format(global_.roadData.base1, global_.roadData.base2))

#----------------------------------------------------------------------------------------------#

def serial_init(port='/dev/ttyUSB0', speed=19200):
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
        print('Could not open port')
        dev = None

    return dev

def serial_recv(dev, size):
    string = dev.read(size).decode()
    return string

def serial_send(dev, string):
    dev.write(string.encode('utf-8'))
