import sys, global_
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QEvent
from PyQt5.QtGui import QColor

from .window import Ui_Watcher
from .workwidget import Ui_Form
from .settingswidget import Ui_SForm
from .telemetrywidget import Ui_TForm

#----------------------------------------------------------------------------------------------#
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

#----------------------------------------------------------------------------------------------#

class QWorkWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_Form(), title=None, layout=None):
        super(QWorkWidget, self).__init__(parent=parent, my_ui=my_ui, title=title, layout=layout)

#----------------------------------------------------------------------------------------------#

class QSettingsWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_SForm(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)
        self.color_red = QColor(255, 0, 0).name()
        self.color_green = QColor(0, 255, 0).name()

    def setChecked(self):
        sender = self.sender()

        if sender == self.ui.EndPointsStop:
            self.ui.EndPointsReverse.setChecked(False)
        elif sender == self.ui.EndPointsReverse:
            self.ui.EndPointsStop.setChecked(False)

#----------------------------------------------------------------------------------------------#

class QTelemetryWidget(QQWidget):
    def __init__(self, parent=None, my_ui=Ui_TForm(), title=None, layout=None):
        QQWidget.__init__(self, parent, my_ui=my_ui, title=title, layout=layout)

#----------------------------------------------------------------------------------------------#

class MainWindow(QMainWindow):
    keyPressed = pyqtSignal(QEvent)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Watcher()
        self.ui.setupUi(self)
        self.setWindowTitle('Watcher')
        self.showFullScreen()

        self.keyPressed.connect(self.on_key)

        self.workWidget = QWorkWidget(layout=self.ui.layoutidontwant)
        self.settingsWidget = QSettingsWidget(layout=self.ui.layoutidontwant)
        self.telemetryWidget = QTelemetryWidget(layout=self.ui.layoutidontwant)

        self.workWidget.show()
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

    def keyPressEvent(self, event):
        super(MainWindow, self).keyPressEvent(event)
        self.keyPressed.emit(event)

    def on_key(self, event):
        # if event.key() == Qt.Key_BracketLeft:
        #     self.workWidget.ui.Velocity.setValue(self.workWidget.ui.Velocity.value() - 5)

        # if event.key() == Qt.Key_BracketRight:
        #     self.workWidget.ui.Velocity.setValue(self.workWidget.ui.Velocity.value() + 5)

        if event.key() == Qt.Key_Q:
            global_.killer.kill()
            sys.exit()

        if event.key() == Qt.Key_1:
            global_.hostData.mode = 1

        if event.key() == Qt.Key_2:
            global_.hostData.mode = 2

        # if event.key() == Qt.Key_A:
        #     global_.hostData.direction = -1

        # if event.key() == Qt.Key_D:
        #     global_.hostData.direction = 1

        # if event.key() == Qt.Key_S:
        #     global_.hostData.mode = 0
        #     # FIXME: CHANGE DIRECTION HERE
        #     self.workWidget.ui.Velocity.setValue(0)

        if event.key() == Qt.Key_W:
            if global_.hostData.set_base == 1:
                global_.hostData.set_base = 2
            else:
                global_.hostData.set_base = 1

        # if event.key() == Qt.Key_R:
        #     global_.hostData.mode = 0
        #     global_.hostData.direction = 0
        #     global_.hostData.set_base = 1
