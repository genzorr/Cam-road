# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'telemetrywidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TForm(object):
    def setupUi(self, TForm):
        TForm.setObjectName("TForm")
        TForm.resize(480, 715)
        self.radioButton = QtWidgets.QRadioButton(TForm)
        self.radioButton.setGeometry(QtCore.QRect(120, 150, 100, 22))
        self.radioButton.setObjectName("radioButton")

        self.retranslateUi(TForm)
        QtCore.QMetaObject.connectSlotsByName(TForm)

    def retranslateUi(self, TForm):
        _translate = QtCore.QCoreApplication.translate
        TForm.setWindowTitle(_translate("TForm", "Form"))
        self.radioButton.setText(_translate("TForm", "RadioButton"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TForm = QtWidgets.QWidget()
    ui = Ui_TForm()
    ui.setupUi(TForm)
    TForm.show()
    sys.exit(app.exec_())
