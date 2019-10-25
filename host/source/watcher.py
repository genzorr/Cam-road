import time, serial, global_
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from lib.data_classes import *
from lib.data_parser import *
from lib.controls import *

#----------------------------------------------------------------------------------------------#
#   A thread used to operate with MBee.
class MbeeThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        # Initialize serial device.
        dev = serial_init()
        while True:
            while dev:
                global_.hostData.acceleration = 3
                global_.hostData.braking = 3

                # Transmitting.
                package = global_.hostData
                data = encrypt_package(package)
                dev.write(data)

                package = global_.specialData
                data = encrypt_package(package)
                dev.write(data)

                # Receiving.
                package = get_decrypt_package(dev)
                if isinstance(package, RTHData):
                    global_.roadData = package


# class MbeeThread_read(QThread):
#     def __init__(self):
#         QThread.__init__(self)

#     def run(self):
#         with open('/dev/ttySAC3', 'rb') as dev:
#             while dev:
#                 package = get_decrypt_package(dev)
#                 if isinstance(package, RTHData):
#                     print('got roadData')
#                     global_.roadData = package

#----------------------------------------------------------------------------------------------#
#   Main thread for getting/throwing data from/to MBee module and for checking all's OK
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
        while True:
            # print('{}\t{}'.format(global_.roadData.base1, global_.roadData.base2))
            time.sleep(2)

#----------------------------------------------------------------------------------------------#
#   A thread used to communitate with remote control.
class ControlThread(QThread):
    def __init__(self, window=None):
        QThread.__init__(self)
        self.controller = Controller()


    def run(self):
        while True:
            print(self.controller.getEncoderValue(0))
            time.sleep(0.5)


#----------------------------------------------------------------------------------------------#

def serial_init(port='/dev/ttySAC3', speed=19200):
    try:
        dev = serial.Serial(
        port=port,
        baudrate=speed,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.2
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