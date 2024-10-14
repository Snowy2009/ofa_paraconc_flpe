#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import sys
from PySide6.QtWidgets import QApplication

from para_conc.core.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
