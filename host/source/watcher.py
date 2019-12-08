import time, global_
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QMutex
from mbee import serialstar
from lib.data_classes import *
from lib.data_parser import *
from lib.controls import *

ACCEL_MAX = 20
BRAKE_MAX = 20
ENC_MAX = 100

#----------------------------------------------------------------------------------------------#
#   Main thread for getting/throwing data from/to MBee module and for checking all's OK
class WatcherThread(QThread):
    def __init__(self, window=None):
        QThread.__init__(self)
        self.alive = True

        if window:
            global_.mbeeThread.RSSI_signal.connect(window.ui.RSSI.display)

        #   Signals to slots connection
        if window.workWidget:
            global_.hostData.acceleration_signal.connect(window.workWidget.ui.Acceleration.setValue)
            global_.hostData.braking_signal.connect(window.workWidget.ui.Braking.setValue)
            global_.hostData.velocity_signal.connect(window.workWidget.ui.Velocity.setValue)
            global_.roadData.coordinate_signal.connect(window.workWidget.ui.Coordinate.setValue)

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


    def run(self):
        while self.alive:
            global_.mbeeThread.RSSI_signal.emit(global_.mbeeThread.RSSI)
            print(global_.hostData.mode, global_.hostData.direction)
            # print(global_.hostData.mode)
            # print('{}\t{}'.format(global_.roadData.base1, global_.roadData.base2))
            # print('{}\t{}\t{}'.format(global_.hostData.acceleration,
            #                         global_.hostData.braking,
            #                         global_.hostData.velocity))
            time.sleep(1)

    def off(self):
        pass


#----------------------------------------------------------------------------------------------#
#   A thread used to communitate with remote control.
MENU = 3
HOME = 0
BASE = 1
LEFT = 15
STOP = 13
RIGHT = 14

def _check_bit(value, bit):
    return True if not (value & (1 << bit)) else False

class ControlThread(QThread):
    changeMenu_sig = pyqtSignal(int)

    def __init__(self, window):
        QThread.__init__(self)
        self.alive = True
        self.controller = Controller()

        self.changeMenu_sig.connect(window.changeMenu)

        self.base_t = 0
        self.menu_t = 0
        self.reset_t = 0
        self.menu = 1

        self.finished.connect(self.controller.off)


    def changeMenu(self):
        if self.menu == 3:
            self.menu = 1
        elif self.menu == 1:
            self.menu = 2
        elif self.menu == 2:
            self.menu = 3
        self.changeMenu_sig.emit(self.menu)


    def run(self):
        while self.alive and self.controller.status:
            self.t = time.time()

            for i in range(1, 3+1):
                encValue = self.controller.getEncoderValue(i)
                self.controller.setIndicator(i, round(encValue/10))

            if (self.t % 10):
                # TODO: add to screen
                self.controller.getBatteryLevel()

            #  Encoders.
            global_.mutex.tryLock(timeout=10)
            global_.hostData.acceleration = self.controller.encoders[1]
            global_.hostData.braking    = self.controller.encoders[2]
            global_.hostData.velocity   = self.controller.encoders[0]
            global_.mutex.unlock()

            global_.hostData.acceleration_signal.emit(self.controller.encoders[1])
            global_.hostData.braking_signal.emit(self.controller.encoders[2])
            global_.hostData.velocity_signal.emit(self.controller.encoders[0])

            ##  Buttons.
            (dummy, value) = self.controller.getButtonValue(0)

            # Stop.
            stop_flag = 0
            t = time.time()
            if (t - self.reset_t > 0.5):
                global_.hostData.mode = -1
                self.reset_t = t

            global_.mutex.tryLock(timeout=10)
            if _check_bit(value, STOP):
                stop_flag = 1
            # if _check_bit(value, LEFT):
            #     if (global_.roadData.mode == 0):
            #         global_.hostData.direction = -1
            #         global_.hostData.mode = 2
            #     elif (global_.roadData.mode == 2):
            #         if (global_.roadData.direction != -1):
            #             global_.hostData.mode = 1
            #             global_.hostData.direction = -1
            # elif _check_bit(value, RIGHT):
            #     if (global_.roadData.mode == 0):
            #         global_.hostData.direction = 1
            #         global_.hostData.mode = 2
            #     elif (global_.roadData.mode == 2):
            #         if (global_.roadData.direction != 1):
            #             global_.hostData.mode = 1
            #             global_.hostData.direction = 1

            elif _check_bit(value, LEFT) and (global_.hostData.velocity != 0):
                if (global_.roadData.mode == 0):
                    global_.hostData.direction = -1
                    global_.hostData.mode = 2

                if (global_.roadData.direction == 1):
                    global_.hostData.mode = 1

            elif _check_bit(value, RIGHT) and (global_.hostData.velocity != 0):
                if (global_.roadData.mode == 0):
                    global_.hostData.direction = 1
                    global_.hostData.mode = 2

                if (global_.roadData.direction == -1):
                    global_.hostData.mode = 1


            global_.mutex.unlock()

            if stop_flag:
                global_.hostData.mode = 0
                global_.hostData.direction = 0
                # self.controller.setEncoderValue(1, 0)
                # self.controller.setIndicator(1, 0)

            # Set base.
            global_.specialData.end_points_reset = False
            global_.hostData.set_base = 0
            global_.mutex.tryLock(timeout=10)
            if _check_bit(value, BASE):
                t = time.time()
                if (t - self.base_t > 2):
                    self.base_t = t
                    if not global_.roadData.base1_set:
                        global_.hostData.set_base = 1
                    elif not global_.roadData.base2_set:
                        global_.hostData.set_base = 2
                print(global_.hostData.set_base, global_.roadData.base1_set, global_.roadData.base2_set)

                if stop_flag: # Reset base points when STOP and BASE buttons pressed.
                    global_.hostData.mode = 0
                    global_.hostData.direction = 0
                    global_.hostData.set_base = 0
                    global_.specialData.end_points_reset = True
            global_.mutex.unlock()

            # Reset hard stop.
            global_.mutex.tryLock(timeout=10)
            global_.specialData.HARD_STOP = False
            if _check_bit(value, HOME):
                if stop_flag:
                    global_.specialData.HARD_STOP = True
                    print('reset')

            # Menu
            if _check_bit(value, MENU):
                t = time.time()
                if (t - self.menu_t > 0.5):
                    self.menu_t = t
                    self.changeMenu()


            # time.sleep(0.2)

    def off(self):
        self.controller.off()


#----------------------------------------------------------------------------------------------#
# /dev/ttySAC4!!
def serial_init(port='/dev/ttySAC4', speed=19200):
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
