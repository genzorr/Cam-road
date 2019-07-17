# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Watcher(object):
    def setupUi(self, Watcher):
        Watcher.setObjectName("Watcher")
        Watcher.resize(480, 800)
        self.centralwidget = QtWidgets.QWidget(Watcher)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 481, 61))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.workButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.workButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.workButton.sizePolicy().hasHeightForWidth())
        self.workButton.setSizePolicy(sizePolicy)
        self.workButton.setObjectName("workButton")
        self.horizontalLayout.addWidget(self.workButton)
        self.settingsButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingsButton.sizePolicy().hasHeightForWidth())
        self.settingsButton.setSizePolicy(sizePolicy)
        self.settingsButton.setObjectName("settingsButton")
        self.horizontalLayout.addWidget(self.settingsButton)
        self.telemetryButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.telemetryButton.sizePolicy().hasHeightForWidth())
        self.telemetryButton.setSizePolicy(sizePolicy)
        self.telemetryButton.setObjectName("telemetryButton")
        self.horizontalLayout.addWidget(self.telemetryButton)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, 59, 481, 741))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.layoutidontwant = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layoutidontwant.setContentsMargins(0, 0, 0, 0)
        self.layoutidontwant.setObjectName("layoutidontwant")
        Watcher.setCentralWidget(self.centralwidget)

        self.retranslateUi(Watcher)
        QtCore.QMetaObject.connectSlotsByName(Watcher)

    def retranslateUi(self, Watcher):
        _translate = QtCore.QCoreApplication.translate
        Watcher.setWindowTitle(_translate("Watcher", "MainWindow"))
        self.workButton.setText(_translate("Watcher", "РАБОТА"))
        self.settingsButton.setText(_translate("Watcher", "НАСТРОЙКИ"))
        self.telemetryButton.setText(_translate("Watcher", "ТЕЛЕМЕТРИЯ"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Watcher = QtWidgets.QMainWindow()
    ui = Ui_Watcher()
    ui.setupUi(Watcher)
    Watcher.show()
    sys.exit(app.exec_())
