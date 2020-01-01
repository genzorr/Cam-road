import time
from PyQt5.QtCore import QThread, pyqtSignal
import logging

import global_
from global_ import get_logger

import serialstar
from lib.data_classes import *
from lib.data_parser import *
from lib.controls import *

ENC_MAX = 100

#----------------------------------------------------------------------------------------------#
#   Main thread for getting/throwing data from/to MBee module and for checking all's OK
class WatcherThread(QThread):
    coordinate_value_sig = pyqtSignal(float)

    def __init__(self):
        QThread.__init__(self)
        self.alive = True
        self.logger = get_logger('Watcher')

        if global_.window:
            global_.mbeeThread.RSSI_signal.connect(global_.window.ui.RSSI.display)
            self.coordinate_value_sig.connect(global_.window.workWidget.ui.Coordinate.setValue)

        #   Signals to slots connection
        if global_.window.workWidget:
            global_.hostData.acceleration_signal.connect(global_.window.workWidget.ui.Acceleration.setValue)
            global_.hostData.braking_signal.connect(global_.window.workWidget.ui.Braking.setValue)
            global_.hostData.velocity_signal.connect(global_.window.workWidget.ui.Velocity.setValue)
            global_.roadData.coordinate_signal.connect(global_.window.workWidget.ui.Coordinate.setValue)

        if global_.window.settingsWidget:
            global_.window.settingsWidget.ui.EnableEndPoints.toggled.connect(global_.specialData.enable_end_points_)
            global_.window.settingsWidget.ui.EndPointsStop.toggled.connect(global_.specialData.end_points_stop_)
            global_.window.settingsWidget.ui.EndPointsReverse.toggled.connect(global_.specialData.end_points_reverse_)
            global_.window.settingsWidget.ui.SoundStop.toggled.connect(global_.specialData.sound_stop_)
            global_.window.settingsWidget.ui.SwapDirection.toggled.connect(global_.specialData.swap_direction_)
            global_.window.settingsWidget.ui.StopAccelerometer.toggled.connect(global_.specialData.stop_accelerometer_)
            global_.window.settingsWidget.ui.LockButtons.toggled.connect(global_.specialData.lock_buttons_)

            '''Stop-reverse end points behavior'''
            global_.window.settingsWidget.ui.EndPointsStop.pressed.connect(global_.window.settingsWidget.setChecked)
            global_.window.settingsWidget.ui.EndPointsReverse.pressed.connect(global_.window.settingsWidget.setChecked)

            global_.window.settingsWidget.ui.EnableEndPoints.toggled.emit(True)
            global_.window.settingsWidget.ui.EndPointsStop.toggled.emit(True)
            global_.window.settingsWidget.ui.EndPointsReverse.toggled.emit(False)
            global_.window.settingsWidget.ui.SoundStop.toggled.emit(False)
            global_.window.settingsWidget.ui.SwapDirection.toggled.emit(False)
            global_.window.settingsWidget.ui.StopAccelerometer.toggled.emit(False)
            global_.window.settingsWidget.ui.LockButtons.toggled.emit(False)

    def run(self):
        while self.alive:
            t = time.time()

            global_.mbeeThread.RSSI_signal.emit(global_.mbeeThread.RSSI)

            global_.window.base1.emit(global_.roadData.base1_set)
            global_.window.base2.emit(global_.roadData.base2_set)

            if (global_.roadData.base1_set and global_.roadData.base2_set):
                length = (global_.roadData.base2 - global_.roadData.base1)
                value = (global_.roadData.coordinate - global_.roadData.base1) / length
                if value > 1:
                    value = 1
                if value < 0:
                    value = 0
                self.coordinate_value_sig.emit(value * 100)
            else:
                self.coordinate_value_sig.emit(0)

            # self.logger.info('')

            # print(global_.hostData.mode, global_.hostData.direction)
            # print(global_.hostData.mode)
            # print('{}\t{}'.format(global_.roadData.base1, global_.roadData.base2))
            # print('{}\t{}\t{}'.format(global_.hostData.acceleration,
            #                         global_.hostData.braking,
            #                         global_.hostData.velocity))
            # print('Watcher', t - time.time())
            time.sleep(0.05)

    def off(self):
        pass


#----------------------------------------------------------------------------------------------#
#   A thread used to communicate with remote control.
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

    def __init__(self):
        QThread.__init__(self)
        self.alive = True
        self.logger = get_logger('Control')

        self.controller = Controller()
        if not self.controller.status:
            self.logger.warning('# Controller init failed')
            return
        else:
            self.logger.info('# Controller OK')

        self.changeMenu_sig.connect(global_.window.changeMenu)

        self.base_t = 0
        self.menu_t = 0
        self.reset_t = 0
        self.menu = 1

        self.finished.connect(self.controller.off)

        global_.hostData.acceleration_signal.emit(0)
        global_.hostData.braking_signal.emit(0)
        global_.hostData.velocity_signal.emit(0)
        for i in range(1, 3+1):
            self.controller.setEncoderValue(i, 0)


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
            time.sleep(0.05)
            self.t = time.time()
            t = time.time()

            for i in range(1, 3+1):
                encValue = self.controller.getEncoderValue(i)
                self.controller.setIndicator(i, round(encValue/10))

            if (self.t % 10):
                # TODO: add to screen
                self.controller.getBatteryLevel()

            (dummy, value) = self.controller.getButtonValue(0)

            #------------------------------------------------------------------#
            global_.mutex.tryLock(timeout=5)

            #  Encoders.
            global_.hostData.acceleration = self.controller.encoders[1]
            global_.hostData.braking  = self.controller.encoders[2]
            global_.hostData.velocity = self.controller.encoders[0]

            ##  Buttons.
            # Stop.
            stop_flag = 0
            t = time.time()
            # if (t - self.reset_t > 1):
            #     global_.hostData.mode = -1
            #     self.reset_t = t

            if not global_.specialData.swap_direction:
                self.left, self.right = LEFT, RIGHT
            else:
                self.left, self.right = RIGHT, LEFT

            if _check_bit(value, STOP):
                stop_flag = 1
                global_.hostData.mode = 0

            elif _check_bit(value, self.left) and (global_.hostData.velocity != 0):
                if global_.roadData.mode == 0:
                    global_.hostData.direction = -1
                    global_.hostData.mode = 2

                if global_.roadData.direction == 1:
                    global_.hostData.mode = 1

            elif _check_bit(value, self.right) and (global_.hostData.velocity != 0):
                if global_.roadData.mode == 0:
                    global_.hostData.direction = 1
                    global_.hostData.mode = 2

                if global_.roadData.direction == -1:
                    global_.hostData.mode = 1

            # Set base.
            global_.specialData.end_points_reset = False
            # global_.hostData.set_base = 0
            if _check_bit(value, BASE):
                self.logger.info('Base pressed {} {}'.format(global_.roadData.base1_set, global_.roadData.base2_set))
                t = time.time()
                if (t - self.base_t) > 2:
                    self.base_t = t
                    if not global_.roadData.base1_set:
                        global_.hostData.set_base = 1
                    elif not global_.roadData.base2_set:
                        global_.hostData.set_base = 2
                # print(global_.hostData.set_base, global_.roadData.base1_set, global_.roadData.base2_set)

                if stop_flag: # Reset base points when STOP and BASE buttons pressed.
                    self.logger.info('Reset end points')
                    global_.hostData.mode = 0
                    global_.hostData.direction = 0
                    global_.hostData.set_base = 0
                    global_.specialData.end_points_reset = True

            # Reset hard stop.
            global_.specialData.HARD_STOP = False
            if _check_bit(value, HOME):
                if stop_flag:
                    global_.specialData.HARD_STOP = True
                    self.logger.info('Hard stop reset')

            global_.mutex.unlock()

            # global_.mutex.tryLock(timeout=5)
            # # t = time.time()
            # global_.mbeeThread.transmit()
            # # print(time.time() - t)
            # global_.hostData.mode = -1
            # global_.mutex.unlock()
            #------------------------------------------------------------------#

            # Menu
            if _check_bit(value, MENU):
                t = time.time()
                if (t - self.menu_t) > 0.5:
                    self.menu_t = t
                    self.changeMenu()

            # print('Control', t - time.time())

    def off(self):
        self.controller.off()
