#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import sys
from PySide6.QtWidgets import QMainWindow, QTextEdit, QLabel, QGridLayout, QVBoxLayout,\
     QHBoxLayout, QPushButton, QRadioButton, QGroupBox, QCheckBox, QLineEdit,QApplication
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont

class SetFreqWindow(QMainWindow):
    save_freq_as_text = Signal()
    save_freq_as_html = Signal()
    def __init__(self, parent=None):
        super(SetFreqWindow, self).__init__(parent)
        self.setWindowTitle('词频统计表')
        self.setGeometry(100, 100, 640, 480)
        self.setWindowIcon(QIcon("./app_data/images/text.png"))
        self.font = QFont("Times New Man",12)
        
        self._fqd_frame = QGroupBox()
        self._fqd_frame_layout = QVBoxLayout() 
        self._browser = QTextEdit(self)
        self._close_btn = QPushButton("关闭")
        self._close_btn.clicked.connect(self.close)
        self._close_btn.setFixedWidth(80)
        self._ctrl_layout = QHBoxLayout()
        self._save_txt_btn = QPushButton("保存为文本")
        self._save_txt_btn.clicked.connect(self.save_freq_as_text)
        self._save_txt_btn.setFixedWidth(120)
        self._save_html_btn = QPushButton("保存为网页")        
        self._save_html_btn.clicked.connect(self.save_freq_as_html)
        self._save_html_btn.setFixedWidth(120)
        self._ctrl_layout.addWidget(self._save_txt_btn)
        self._ctrl_layout.addWidget(self._save_html_btn)
        self._ctrl_layout.addWidget(self._close_btn)
        self._fqd_frame_layout.addWidget(self._browser)
        self._fqd_frame_layout.addLayout(self._ctrl_layout)
        self._fqd_frame.setLayout(self._fqd_frame_layout)
        
        self._browser.setReadOnly(True)
        self._browser.setContextMenuPolicy(Qt.NoContextMenu)
        self._browser.setStyleSheet("QTextEdit{background-color:%s}"% ("WhiteSmoke"))
        self.setCentralWidget(self._fqd_frame)

    def set_title(self, title):
        self.setWindowTitle(title)
        self._data_title = title

    def set_text(self, text):
        self._browser.setText(text)

    def set_html(self, html):
        self._browser.setHtml(html)

    def set_geometry (self, hm, vm, length, height):
        self.setGeometry(int(hm),int(vm),int(length),int(height))

    def set_icon(self, icon_path):
        self.setWindowIcon(QIcon(icon_path))        

    def resizeFontUp(self):
        if self.font.pointSize() >= 16:
            pass
        else:
            font_size = self.font.pointSize()+1
            font_family = self.font.family()
            self.font = QFont(font_family, font_size)
            self._browser.setFont(self.font)
    
    def resizeFontDown(self):
        if self.font.pointSize() <= 8:
            pass
        else:
            font_size = self.font.pointSize()-1
            font_family = self.font.family()
            self.font = QFont(font_family, font_size)
            self._browser.setFont(self.font)
        
    def keyReleaseEvent(self, event):
        modifiers = event.modifiers()
        if modifiers == (Qt.ControlModifier) and event.key()==Qt.Key_Up:
            self.resizeFontUp()
        if modifiers == (Qt.ControlModifier) and event.key()==Qt.Key_Down:
            self.resizeFontDown()
