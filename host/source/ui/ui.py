import sys
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
                        self.ui.SoundStop, self.ui.SwapDirection, self.ui.StopAccelerometer]

        self.ui.verticalLayout.setAlignment(Qt.AlignTop)

    # def setChecked(self):
    #     sender = self.sender()

    #     if sender == self.ui.EndPointsStop:
    #         if sender.isDown():
    #             self.ui.EndPointsReverse.setChecked(True)
    #         else:
    #             self.ui.EndPointsReverse.setChecked(False)
    #     elif sender == self.ui.EndPointsReverse:
    #         if sender.isDown():
    #             self.ui.EndPointsStop.setChecked(True)
    #         else:
    #             self.ui.EndPointsStop.setChecked(False)
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
    # keyPressed = pyqtSignal(QEvent)
    base1 = pyqtSignal(bool)
    base2 = pyqtSignal(bool)

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

        # self.workWidget.hide()
        # self.settingsWidget.hide()
        # self.telemetryWidget.show()

        # Signals to use menu buttons and shutdown button.
        # self.ui.workButton.clicked.connect(self.buttonClicked)
        # self.ui.settingsButton.clicked.connect(self.buttonClicked)
        # self.ui.telemetryButton.clicked.connect(self.buttonClicked)
        self.settingsWidget.ui.Shutdown.clicked.connect(self.buttonClicked)

        self.base1.connect(global_.specialData.base1_)
        self.base2.connect(global_.specialData.base2_)

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
