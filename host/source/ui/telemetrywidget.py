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
        self.verticalLayoutWidget = QtWidgets.QWidget(TForm)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 481, 711))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        self.text = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text.sizePolicy().hasHeightForWidth())
        self.text.setSizePolicy(sizePolicy)
        self.text.setObjectName("text")
        self.layout.addWidget(self.text)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout.setContentsMargins(20, 10, -1, -1)
        self.formLayout.setObjectName("formLayout")
        self.sig_stop = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.sig_stop.setText("")
        self.sig_stop.setCheckable(True)
        self.sig_stop.setObjectName("sig_stop")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.sig_stop)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label)
        self.sig_ret1 = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.sig_ret1.setText("")
        self.sig_ret1.setCheckable(True)
        self.sig_ret1.setObjectName("sig_ret1")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.sig_ret1)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_2)
        self.sig_ret2 = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.sig_ret2.setText("")
        self.sig_ret2.setCheckable(True)
        self.sig_ret2.setObjectName("sig_ret2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.sig_ret2)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_4)
        self.layout.addLayout(self.formLayout)

        self.retranslateUi(TForm)
        QtCore.QMetaObject.connectSlotsByName(TForm)

    def retranslateUi(self, TForm):
        _translate = QtCore.QCoreApplication.translate
        TForm.setWindowTitle(_translate("TForm", "Form"))
        self.label.setText(_translate("TForm", "ОСТАНОВ"))
        self.label_2.setText(_translate("TForm", "ВОЗВРАТ В ТОЧКУ 1"))
        self.label_3.setText(_translate("TForm", "ВОЗВРАТ В ТОЧКУ 2"))
        self.label_4.setText(_translate("TForm", "ПРИ ПОТЕРЕ СИГНАЛА"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TForm = QtWidgets.QWidget()
    ui = Ui_TForm()
    ui.setupUi(TForm)
    TForm.show()
    sys.exit(app.exec_())
