#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from ui_main import *

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
