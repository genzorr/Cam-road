import sys
import os.path as path
import hjson
import global_
from global_ import addStyleSheet, styleChangeProperty

from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QWidget

from .settingswidget import Ui_SForm
from .telemetrywidget import Ui_TForm
from .window import Ui_Watcher
from .workwidget import Ui_Form

# ---------------------------------------------------------------------------------------------- #
#   Base class
class QQWidget(QWidget):
    def __init__(self, parent=None, my_ui=None, title=None, layout=None):
        super(QQWidget, self).__init__(parent)
        self.ui = my_ui
        self.ui.setupUi(self)
        self.set_window_title(title)
        self.set_layout(layout)

    def set_window_title(self, title):
        self.setWindowTitle(str(title))

    def set_layout(self, layout):
        layout.addWidget(self)

# ---------------------------------------------------------------------------------------------- #

class QWorkWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_Form(), title=None, layout=None):
        super(QWorkWidget, self).__init__(parent=parent, my_ui=my_ui, title=title, layout=layout)

        self.ui.Base1.setCheckable(False)
        self.ui.Base2.setCheckable(False)

        self.ui.Base1.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.ui.Base2.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.ui.Base1.setText('1')
        self.ui.Base2.setText('2')

# ---------------------------------------------------------------------------------------------- #

class QSettingsWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_SForm(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)

        self.buttons = [self.ui.EnableEndPoints, self.ui.EndPointsStop, self.ui.EndPointsReverse,\
                        self.ui.SwapDirection, self.ui.StopAccelerometer]

        self.ui.verticalLayout.setAlignment(Qt.AlignTop)

# ---------------------------------------------------------------------------------------------- #

class QTelemetryWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_TForm(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)

        self.ui.layout.setAlignment(Qt.AlignTop)

        style = ''
        style += 'QSpinBox::up-button {subcontrol-position: top right; width: 30px; height: 30px; padding: 5px; margin: 5px;} '
        style += 'QSpinBox::down-button {subcontrol-position: bottom right; width: 30px; height: 30px; padding: 5px; margin: 5px;} '
        addStyleSheet(self.ui.stop_time, 'QSpinBox', style)
        self.ui.stop_time.setMinimumSize(QSize(120, 100))

#----------------------------------------------------------------------------------------------#

class MainWindow(QMainWindow):
    base1 = pyqtSignal(bool)
    base2 = pyqtSignal(bool)

    coordinate_value_sig = pyqtSignal(float)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)
        self.setWindowTitle('Watcher')

        self.workWidget = QWorkWidget(layout=self.ui.layoutidontwant)
        self.settingsWidget = QSettingsWidget(layout=self.ui.layoutidontwant)
        self.telemetryWidget = QTelemetryWidget(layout=self.ui.layoutidontwant)

        self.workWidget.show()
        styleChangeProperty(self.ui.workButton, 'background-color', 'rgb(255,140,0)')
        self.settingsWidget.hide()
        self.telemetryWidget.hide()

        self.ui.horizontalLayout.removeWidget(self.ui.battery)
        self.ui.battery.deleteLater()
        self.ui.battery = None

        self.settingsWidget.ui.verticalLayout.removeWidget(self.settingsWidget.ui.widget_5)
        self.settingsWidget.ui.widget_5.deleteLater()
        self.settingsWidget.ui.widget_5 = None

        # Signals to use menu buttons and shutdown button.
        self.settingsWidget.ui.Shutdown.clicked.connect(self.buttonClicked)

        self.base1.connect(global_.specialData.base1_)
        self.base2.connect(global_.specialData.base2_)

        self.coordinate_value_sig.connect(self.workWidget.ui.Coordinate.setValue)

        self.showFullScreen()

    def changeMenu(self, num):
        self.workWidget.hide()
        styleChangeProperty(self.ui.workButton, 'background-color', 'white')
        self.settingsWidget.hide()
        styleChangeProperty(self.ui.settingsButton, 'background-color', 'white')
        self.telemetryWidget.hide()
        styleChangeProperty(self.ui.telemetryButton, 'background-color', 'white')

        if num == 1:
            self.workWidget.show()
            styleChangeProperty(self.ui.workButton, 'background-color', 'rgb(255,140,0)')
        elif num == 2:
            self.settingsWidget.show()
            styleChangeProperty(self.ui.settingsButton, 'background-color', 'rgb(255,140,0)')
        elif num == 3:
            self.telemetryWidget.show()
            styleChangeProperty(self.ui.telemetryButton, 'background-color', 'rgb(255,140,0)')
        else:
            print('# Invalid menu value')
            pass

    def buttonClicked(self):
        sender = self.sender()

        if sender == self.ui.workButton:
            self.settingsWidget.hide()
            self.telemetryWidget.hide()
            self.workWidget.show()

        if sender == self.ui.settingsButton:
            self.workWidget.hide()
            self.telemetryWidget.hide()
            self.settingsWidget.show()

        if sender == self.ui.telemetryButton:
            self.workWidget.hide()
            self.settingsWidget.hide()
            self.telemetryWidget.show()

        if sender == self.settingsWidget.ui.Shutdown:
            global_.killer.kill()
            sys.exit()

    def setButtonValue(self, button, value):
        if value == 1:
            button.setChecked(True)
        else:
            button.toggled.emit(False)

    def getButtonValue(self, button):
        return 1 if button.isChecked() else 0

    def saveSettings(self):
        sig_lose_value = 0
        if self.getButtonValue(self.telemetryWidget.ui.sig_stop) == 1:
            sig_lose_value = 0
        elif self.getButtonValue(self.telemetryWidget.ui.sig_ret1) == 1:
            sig_lose_value = 1
        else:
            sig_lose_value = 2

        config = {
            'ACCEL': global_.hostData.acceleration,
            'BRAKING': global_.hostData.braking,
            'END_POINTS': self.getButtonValue(self.settingsWidget.ui.EnableEndPoints),
            'END_POINTS_STOP': self.getButtonValue(self.settingsWidget.ui.EndPointsStop),
            'SWAP': self.getButtonValue(self.settingsWidget.ui.SwapDirection),
            'STOP_ACCEL': self.getButtonValue(self.settingsWidget.ui.StopAccelerometer),
            'LOCK': self.getButtonValue(self.settingsWidget.ui.LockButtons),
            'SIG_LOSE': sig_lose_value,
            'STOP_TIME': self.telemetryWidget.ui.stop_time.value()
        }

        filepath = path.abspath(__file__)
        dirname = path.dirname(filepath)
        with open(dirname + '/settings.json', 'w') as f:
            hjson.dump(config, f)

    def loadSettings(self):
        filepath = path.abspath(__file__)
        dirname = path.dirname(filepath)
        config = None
        with open(dirname + '/settings.json', 'r') as f:
            config = hjson.loads(f.read())

        if not config:
            return

        global_.hostData.acceleration = config['ACCEL']
        global_.controlThread.controller.setEncoderValue(2, config['ACCEL'])
        global_.hostData.braking = config['BRAKING']
        global_.controlThread.controller.setEncoderValue(3, config['BRAKING'])

        self.setButtonValue(self.settingsWidget.ui.EnableEndPoints, config['END_POINTS'])
        self.setButtonValue(self.settingsWidget.ui.EndPointsStop, config['END_POINTS_STOP'])
        self.setButtonValue(self.settingsWidget.ui.EndPointsReverse, 1 - config['END_POINTS_STOP'])
        # self.buttonSetValue(self.settingsWidget.ui.SoundStop, config['LOCK'])
        self.setButtonValue(self.settingsWidget.ui.SwapDirection, config['SWAP'])
        self.setButtonValue(self.settingsWidget.ui.StopAccelerometer, config['STOP_ACCEL'])
        self.setButtonValue(self.settingsWidget.ui.LockButtons, config['LOCK'])

        self.setButtonValue(self.telemetryWidget.ui.sig_stop, 0)
        self.setButtonValue(self.telemetryWidget.ui.sig_ret1, 0)
        self.setButtonValue(self.telemetryWidget.ui.sig_ret2, 0)
        if (config['SIG_LOSE'] == 0):
            self.setButtonValue(self.telemetryWidget.ui.sig_stop, 1)
        elif (config['SIG_LOSE'] == 1):
            self.setButtonValue(self.telemetryWidget.ui.sig_ret1, 1)
        else:
            self.setButtonValue(self.telemetryWidget.ui.sig_ret2, 1)

        self.telemetryWidget.ui.stop_time.setValue(config['STOP_TIME'])

    def rssi_value_slot(self, value):
        if value is None or value == 0.0:
            global_.window.ui.RSSI.setStyleSheet("background-color: gray; color: black")
            # styleChangeProperty(global_.window.ui.RSSI, 'color', 'black')
            # styleChangeProperty(global_.window.ui.RSSI, 'background-color', 'gray')
        elif value < -90:
            global_.window.ui.RSSI.setStyleSheet("background-color: black; color: white")
            # styleChangeProperty(global_.window.ui.RSSI, 'color', 'white')
            # styleChangeProperty(global_.window.ui.RSSI, 'background-color', 'black')
        elif value < -80:
            global_.window.ui.RSSI.setStyleSheet("background-color: red; color: black")
            # styleChangeProperty(global_.window.ui.RSSI, 'color', 'black')
            # styleChangeProperty(global_.window.ui.RSSI, 'background-color', 'red')
        elif value < -60:
            global_.window.ui.RSSI.setStyleSheet("background-color: yellow; color: black")
            # styleChangeProperty(global_.window.ui.RSSI, 'color', 'black')
            # styleChangeProperty(global_.window.ui.RSSI, 'background-color', 'yellow')
        else:
            global_.window.ui.RSSI.setStyleSheet("background-color: green; color: black")
            # styleChangeProperty(global_.window.ui.RSSI, 'color', 'black')
            # styleChangeProperty(global_.window.ui.RSSI, 'background-color', 'green')

    def road_battery_value_slot(self, value):
        # If motor is offed, display all elements in gray.
        if global_.roadData.mode != -1:
            if value < 20:
                global_.window.ui.battery_road.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: red}')
                global_.window.workWidget.ui.Acceleration.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: red}')
                global_.window.workWidget.ui.Braking.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: red}')
                global_.window.workWidget.ui.Velocity.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: red}')
                global_.window.workWidget.ui.Coordinate.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: red}')
            else:
                global_.window.ui.battery_road.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: QColor (0,0,180)}')
                global_.window.workWidget.ui.Acceleration.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: QColor (0,0,180)}')
                global_.window.workWidget.ui.Braking.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: QColor (0,0,180)}')
                global_.window.workWidget.ui.Velocity.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: QColor (0,0,180)}')
                global_.window.workWidget.ui.Coordinate.setStyleSheet(
                    'QProgressBar {text-align: center} QProgressBar::chunk {background-color: QColor (0,0,180)}')
        else:
            global_.window.ui.battery_road.setStyleSheet(
                'QProgressBar {text-align: center} QProgressBar::chunk {background-color: gray}')
            global_.window.workWidget.ui.Acceleration.setStyleSheet(
                'QProgressBar {text-align: center} QProgressBar::chunk {background-color: gray}')
            global_.window.workWidget.ui.Braking.setStyleSheet(
                'QProgressBar {text-align: center} QProgressBar::chunk {background-color: gray}')
            global_.window.workWidget.ui.Velocity.setStyleSheet(
                'QProgressBar {text-align: center} QProgressBar::chunk {background-color: gray}')
            global_.window.workWidget.ui.Coordinate.setStyleSheet(
                'QProgressBar {text-align: center} QProgressBar::chunk {background-color: gray}')

