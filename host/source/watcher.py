import time

from PyQt5.QtCore import QThread, pyqtSignal

import global_
from global_ import get_logger, styleChangeProperty, addStyleSheet
from lib.controls import Controller

# Main thread for getting/throwing data from/to MBee module and for checking all's OK
class WatcherThread(QThread):
    road_battery_sig = pyqtSignal(float)
    rssi_value_sig = pyqtSignal(float)

    def __init__(self):
        QThread.__init__(self)
        self.alive = True
        self.logger = get_logger('Watcher')

        if global_.window:
            self.road_battery_sig.connect(global_.window.ui.battery_road.setValue)
            self.road_battery_sig.connect(global_.window.road_battery_value_slot)
            self.rssi_value_sig.connect(global_.window.rssi_value_slot)

        # Connect signals to slots.
        if global_.window.workWidget:
            global_.hostData.acceleration_signal.connect(global_.window.workWidget.ui.Acceleration.setValue)
            global_.hostData.braking_signal.connect(global_.window.workWidget.ui.Braking.setValue)
            global_.hostData.velocity_signal.connect(global_.window.workWidget.ui.Velocity.setValue)
            global_.roadData.coordinate_signal.connect(global_.window.workWidget.ui.Coordinate.setValue)

        if global_.window.settingsWidget:
            global_.window.settingsWidget.ui.EndPointsReverse.setAutoExclusive(True)
            global_.window.settingsWidget.ui.EndPointsStop.setAutoExclusive(True)
            global_.window.settingsWidget.ui.EnableEndPoints.setFocusPolicy(False)

            global_.window.settingsWidget.ui.EnableEndPoints.toggled.connect(global_.specialData.enable_end_points_)
            global_.window.settingsWidget.ui.EndPointsStop.toggled.connect(global_.specialData.end_points_stop_)
            global_.window.settingsWidget.ui.EndPointsReverse.toggled.connect(global_.specialData.end_points_reverse_)
            global_.window.settingsWidget.ui.SoundStop.toggled.connect(global_.specialData.sound_stop_)
            global_.window.settingsWidget.ui.SwapDirection.toggled.connect(global_.specialData.swap_direction_)
            global_.window.settingsWidget.ui.StopAccelerometer.toggled.connect(global_.specialData.stop_accelerometer_)
            global_.window.settingsWidget.ui.LockButtons.toggled.connect(global_.specialData.lock_buttons_)

            global_.window.telemetryWidget.ui.sig_stop.setAutoExclusive(True)
            global_.window.telemetryWidget.ui.sig_ret1.setAutoExclusive(True)
            global_.window.telemetryWidget.ui.sig_ret2.setAutoExclusive(True)
            global_.window.telemetryWidget.ui.sig_stop.toggled.connect(global_.specialData.sig_stop_)
            global_.window.telemetryWidget.ui.sig_ret1.toggled.connect(global_.specialData.sig_ret1_)
            global_.window.telemetryWidget.ui.sig_ret2.toggled.connect(global_.specialData.sig_ret2_)

    def run(self):
        while self.alive:
            t = time.time()

            global_.mutex.tryLock(timeout=1)

            if int(t) % 5 == 0:
                # Update progress bars.
                self.rssi_value_sig.emit(global_.mbeeThread.RSSI)
                v = global_.roadData.voltage
                self.road_battery_sig.emit(v)

            global_.window.base1.emit(global_.roadData.base1_set)
            global_.window.base2.emit(global_.roadData.base2_set)

            # Show coordinate on progress bar.
            if global_.roadData.base1_set and global_.roadData.base2_set:
                length = (global_.roadData.base2 - global_.roadData.base1)
                value = (global_.roadData.coordinate - global_.roadData.base1) / length
                if value > 1:
                    value = 1
                if value < 0:
                    value = 0
                global_.window.coordinate_value_sig.emit(value * 100)
            else:
                global_.window.coordinate_value_sig.emit(0)
            global_.mutex.unlock()

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
    finished = pyqtSignal(int)

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

        self.t = 0
        self.menu_t = 0
        self.home_t = 0
        self.base_t = 0
        self.left_t = 0
        self.right_t = 0
        self.stop_t = 0
        self.reset_t = 0
        self.menu = 1

        self.state = []
        self.state_prev = []
        self.state_prev_t = 0
        global_.newHTR = False

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
                enc_value = self.controller.getEncoderValue(i)
                self.controller.setIndicator(i, round(enc_value/10))

            if self.t % 10:
                # TODO: add to screen
                self.controller.getBatteryLevel()

            (dummy, value) = self.controller.getButtonValue(0)

            #------------------------------------------------------------------#
            global_.mutex.tryLock(timeout=1)

            # Encoders.
            global_.hostData.acceleration = self.controller.encoders[1]
            global_.hostData.braking  = self.controller.encoders[2]
            global_.hostData.velocity = self.controller.encoders[0]

            # Buttons.
            stop_flag = 0
            t = time.time()

            if not global_.specialData.swap_direction:  # Swap direction if flag is set.
                self.left, self.right = LEFT, RIGHT
            else:
                self.left, self.right = RIGHT, LEFT

            if _check_bit(value, STOP):
                if (t - self.stop_t) > 1:
                    self.stop_t = t
                    stop_flag = 1
                    global_.hostData.mode = 0

            elif _check_bit(value, self.left):
                if (t - self.left_t) > 1:
                    self.left_t = t
                    global_.hostData.direction = -1

            elif _check_bit(value, self.right):
                if (t - self.right_t) > 1:
                    self.right_t = t
                    global_.hostData.direction = 1

            # Set base.
            if _check_bit(value, BASE):
                if stop_flag:   # Reset base points when STOP and BASE buttons pressed.
                    self.logger.info('Reset end points')
                    global_.specialData.end_points_reset = True

                elif (t - self.base_t) > 1:
                    self.logger.info('Base pressed {} {}'.format(global_.roadData.base1_set, global_.roadData.base2_set))
                    self.base_t = t
                    global_.hostData.set_base = 1

            # Reset hard stop.
            if _check_bit(value, HOME):
                if (t - self.home_t > 1):
                    self.home_t = t
                    global_.specialData.motor = True
                    self.logger.info('Motor off')

            global_.mutex.unlock()

            self.state = [global_.hostData.velocity, global_.hostData.acceleration, global_.hostData.braking,\
                            global_.hostData.mode, global_.hostData.direction, global_.hostData.set_base,\
                            global_.specialData.end_points_reset, global_.specialData.motor]

            # Check state lists and update flag if it's changed.
            if (t - self.state_prev_t > 3) or (self.state != self.state_prev):
                global_.newHTR = True
                self.state_prev = self.state
                self.state_prev_t = t

            # Menu.
            if _check_bit(value, MENU):
                if (t - self.menu_t) > 0.5:
                    self.menu_t = t
                    self.changeMenu()

    def off(self):
        self.controller.off()
