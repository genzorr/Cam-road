from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from window import Ui_Watcher
from workwidget import Ui_Form
from settingswidget import Ui_SForm
from telemetrywidget import Ui_TForm

#----------------------------------------------------------------------------------------------#
#   Base class
class QQWidget(QWidget):
    def __init__(self, parent=None, my_ui=None, title=None, layout=None):
        QWidget.__init__(self, parent)
        self.ui = my_ui
        self.ui.setupUi(self)
        self.set_window_title(title)
        self.set_layout(layout)

    def set_window_title(self, title):
        self.setWindowTitle(str(title))

    def set_layout(self, layout):
        layout.addWidget(self)

#----------------------------------------------------------------------------------------------#

class QWorkWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_Form(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)
        self._acceleration = 0.0
        self._braking = 0.0
        self._velocity = 0.0
        self._coordinate = 0.0

        # self.acceleration_signal.connect(self.ui.Acceleration.setValue)
        # self.braking_signal.connect(self.ui.Braking.setValue)
        # self.velocity_signal.connect(self.ui.Velocity.setValue)
        # self.coordinate_signal.connect(self.ui.Coordinate.setValue)

    @property       # Acceleration value property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        self._acceleration = value

    @property       # Braking value property
    def braking(self):
        return self._braking

    @braking.setter
    def braking(self, value):
        self._braking = value

    @property       # Velocity value property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self._velocity = value

    @property       # Coordinate value property
    def coordinate(self):
        return self._coordinate

    @coordinate.setter
    def coordinate(self, value):
        self._coordinate = value

#----------------------------------------------------------------------------------------------#

class QSettingsWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_SForm(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)

#----------------------------------------------------------------------------------------------#

class QTelemetryWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_TForm(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)

#----------------------------------------------------------------------------------------------#

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)
        self.setWindowTitle('Watcher')

        self.workWidget = QWorkWidget(layout=self.ui.layoutidontwant)
        self.settingsWidget = QSettingsWidget(layout=self.ui.layoutidontwant)
        self.telemetryWidget = QTelemetryWidget(layout=self.ui.layoutidontwant)

        self.workWidget.hide()
        self.settingsWidget.hide()
        self.telemetryWidget.hide()

        #   Signals
        self.ui.workButton.clicked.connect(self.buttonClicked)
        self.ui.settingsButton.clicked.connect(self.buttonClicked)
        self.ui.telemetryButton.clicked.connect(self.buttonClicked)


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
