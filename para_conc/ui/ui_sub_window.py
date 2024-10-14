#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

from PySide6.QtWidgets import QMainWindow, QTextEdit, QLabel, QGridLayout, QVBoxLayout,\
     QHBoxLayout, QPushButton, QRadioButton, QGroupBox, QCheckBox, QLineEdit
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont

class SubWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SubWindow, self).__init__(parent)
        self.setWindowTitle('全文')
        self.setGeometry(100, 100, 640, 480)
        self.setWindowIcon(QIcon("./app_data/images/text.png"))
        self._browser = QTextEdit(self)
        self.font = QFont("Times New Man",12)

        self._browser.setReadOnly(True)
        self._browser.setContextMenuPolicy(Qt.NoContextMenu)
        self._browser.setStyleSheet("QTextEdit{background-color:%s}"% ("WhiteSmoke"))
        self.setCentralWidget(self._browser)

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_text(self, text):
        self._browser.setText(text)

    def set_html(self, html):
        self._browser.setHtml(html)

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

class VocWindow(QMainWindow):
    def __init__(self, parent=None):
        super(VocWindow, self).__init__(parent)
        self.setWindowTitle('词频统计')
        self.setWindowIcon(QIcon("./app_data/images/freq.png"))
        self.setGeometry(100, 100, 640, 480)
        
        self._voc_frame = QGroupBox()
        self._voc_frame_layout = QVBoxLayout() 
        self._browser = QTextEdit(self)
        self._close_btn = QPushButton("关闭")
        self._close_btn.clicked.connect(self.close)
        self._close_btn.setFixedWidth(80)        
        self._voc_frame_layout.addWidget(self._browser)
        self._voc_frame_layout.addWidget(self._close_btn, alignment=Qt.AlignCenter)
        self._voc_frame.setLayout(self._voc_frame_layout)
        
        self._browser.setReadOnly(True)
        self._browser.setContextMenuPolicy(Qt.NoContextMenu)
        self._browser.setStyleSheet("QTextEdit{background-color:%s}"% ("WhiteSmoke"))
        self.setCentralWidget(self._voc_frame)

    def set_title(self, title):
        self.setWindowTitle(title)

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

class SetVocWindow(QMainWindow):
    clear_current_results = Signal()
    freq_print_request = Signal(dict)
    def __init__(self, parent=None):
        super(SetVocWindow, self).__init__(parent)
        self._filter_choices = {}
        self.setWindowTitle('词频设置')
        self.setGeometry(100, 100, 200, 100)
        self._browser= QGroupBox()
        self._browser_layout = QVBoxLayout()
        self._frame_zh = QGroupBox("中文词频免显选项")
        self._frame_zh_layout = QGridLayout()
        self._frame_en = QGroupBox("英文词频免显选项")
        self._frame_en_layout = QGridLayout()
        self._zh_punc_box = QCheckBox("标点符号")
        self._zh_num_box = QCheckBox("阿拉伯数字")
        self._zh_stopword_box = QCheckBox("停用词表")
        self._zh_english_box = QCheckBox("英文单词")
        self._zh_freq_label = QLabel("小于词频：")
        self._zh_freq_box = QLineEdit("1")
        self._zh_length_label = QLabel("小于词长：")
        self._zh_length_box = QLineEdit("1")
        self._frame_zh_layout.addWidget(self._zh_stopword_box, 0, 0)
        self._frame_zh_layout.addWidget(self._zh_punc_box, 0, 1)        
        self._frame_zh_layout.addWidget(self._zh_freq_label, 0, 2)
        self._frame_zh_layout.addWidget(self._zh_freq_box, 0, 3)
        self._frame_zh_layout.addWidget(self._zh_num_box, 1, 0)
        self._frame_zh_layout.addWidget(self._zh_english_box, 1, 1)
        self._frame_zh_layout.addWidget(self._zh_length_label, 1, 2)
        self._frame_zh_layout.addWidget(self._zh_length_box, 1, 3)
        
        self._en_punc_box = QCheckBox("标点符号")
        self._en_num_box = QCheckBox("阿拉伯数字")
        self._en_stopword_box = QCheckBox("停用词表")        
        self._en_freq_label = QLabel("小于词频：")
        self._en_freq_box = QLineEdit("1")
        self._en_length_label = QLabel("小于词长：")
        self._en_length_box = QLineEdit("1")
        self._frame_en_layout.addWidget(self._en_stopword_box, 0, 0)
        self._frame_en_layout.addWidget(self._en_punc_box, 0, 1)        
        self._frame_en_layout.addWidget(self._en_freq_label, 0, 2)
        self._frame_en_layout.addWidget(self._en_freq_box, 0, 3)
        self._frame_en_layout.addWidget(self._en_num_box, 1, 0)
        self._frame_en_layout.addWidget(self._en_length_label, 1, 2)
        self._frame_en_layout.addWidget(self._en_length_box, 1, 3)

        self._freq_lang = QGroupBox()
        self._freq_lang_layout = QGridLayout()
        self._freq_lang_label = QLabel("词频类型：")
        self._freq_lang_zh = QRadioButton("中文词频")
        self._freq_lang_en = QRadioButton("英文词频")
        self._freq_lang_zh.setChecked(True)
        self._freq_lang_layout.addWidget(self._freq_lang_label, 0,0)
        self._freq_lang_layout.addWidget(self._freq_lang_zh, 0,1)
        self._freq_lang_layout.addWidget(self._freq_lang_en, 0,2)
        self._freq_lang.setLayout(self._freq_lang_layout)

        self._freq_scope = QGroupBox()
        self._freq_scope_layout = QGridLayout()
        self._freq_scope_label = QLabel("语料范围：")
        self._freq_scope_current = QRadioButton("当前语料")
        self._freq_scope_selected = QRadioButton("所选语料")
        self._freq_scope_all = QRadioButton("全部语料")
        self._freq_scope_current.setChecked(True)
        self._freq_scope_layout.addWidget(self._freq_scope_label, 0,0)
        self._freq_scope_layout.addWidget(self._freq_scope_current, 0,1)
        self._freq_scope_layout.addWidget(self._freq_scope_selected, 0,2)
        self._freq_scope_layout.addWidget(self._freq_scope_all, 0,3)
        self._freq_scope.setLayout(self._freq_scope_layout)

        self._ok_button = QPushButton("开始统计")
        self._ok_button.clicked[bool].connect(self.send_print_request) 
        self._frame_zh.setLayout(self._frame_zh_layout)
        self._frame_en.setLayout(self._frame_en_layout)
        self._browser_layout.addWidget(self._frame_zh)
        self._browser_layout.addWidget(self._frame_en)
        self._browser_layout.addWidget(self._freq_scope)
        self._browser_layout.addWidget(self._freq_lang)
        self._browser_layout.addWidget(self._ok_button, alignment = Qt.AlignCenter)
        self._browser.setLayout(self._browser_layout)
        self.setCentralWidget(self._browser)
        self.setWindowIcon(QIcon("./app_data/images/freq.png"))
        
    def send_print_request(self):
        filter_opts = self.get_filter_options()
        self.freq_print_request.emit(filter_opts)
        self.close()
        
    def get_filter_options(self):
        check_state = {}
        check_state["stop"]=[]        
        check_state['off']=[]
        check_state["freq"]={}
        check_state["length"]={}
        check_state["freq"]['zh']=1
        check_state["freq"]['en']=1
        check_state["length"]['zh']=1
        check_state["length"]['en']=1
        check_state["lang"]=0
        check_state["scope"]=0
        if self._zh_stopword_box.isChecked():
            check_state["stop"].append('z_stop')
        if self._zh_punc_box.isChecked():
            check_state["off"].append('z_punc')
        if self._zh_num_box.isChecked():
            check_state["off"].append('z_arab')
        if self._zh_english_box.isChecked():
            check_state["off"].append('z_alien')
        if self._freq_lang_en.isChecked():
            check_state["lang"]=1
        if self._freq_scope_selected.isChecked():
            check_state["scope"]=1
        if self._freq_scope_all.isChecked():
            check_state["scope"]=2            
        freq_num = self._zh_freq_box.text()
        try:
            if int(freq_num) > 1:
                check_state["freq"]['zh']=int(freq_num)              
        except:
            pass
        length_num = self._zh_length_box.text()
        try:
            if int(length_num) > 1:
                check_state["length"]['zh']=int(length_num)              
        except:
            pass
        if self._en_stopword_box.isChecked():
            check_state["stop"].append('e_stop')
        if self._en_punc_box.isChecked():
            check_state['off'].append('e_punc')
        if self._en_num_box.isChecked():
            check_state['off'].append('e_arab')
        freq_num = self._en_freq_box.text()
        try:
            if int(freq_num) > 1:
                check_state["freq"]['en']=int(freq_num)
        except:
            pass
        length_num = self._en_length_box.text()
        try:
            if int(length_num) > 1:
                check_state["length"]['en']=int(length_num)              
        except:
            pass
        self._filter_choices = check_state
        return check_state

class TermWindow(QMainWindow):
    term_saving = Signal(str)
    def __init__(self, dict_file, parent=None):
        super(TermWindow, self).__init__(parent)
        self.setWindowTitle('文本文件')
        self.setFixedSize(640, 480)
        self.setWindowIcon(QIcon("./app_data/images/term.png"))
        self.dict_file = dict_file
        button_max = 80

        self._main = QGroupBox()
        self._main_layout = QVBoxLayout()
        
        self._browser = QTextEdit(self)      

        self._button_layout = QHBoxLayout()
        self._save_button = QPushButton("保存语料")
        self._save_button.clicked[bool].connect(self.save_file)
        self._save_button.setFixedWidth(button_max)
        self._quit_button = QPushButton("关闭退出")        
        self._quit_button.clicked[bool].connect(self.close)
        self._quit_button.setFixedWidth(button_max)
        self._button_layout.addWidget(self._save_button)
        self._button_layout.addWidget(self._quit_button)

        self._main_layout.addWidget(self._browser)
        self._main_layout.addLayout(self._button_layout)
        self._main.setLayout(self._main_layout)
        self.setCentralWidget(self._main)

        self.set_text(self.dict_file)

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_icon(self, icon_path):
        self.setWindowIcon(QIcon(icon_path))

    def set_text(self, file_to_open):
        with open(file_to_open, "rt", encoding = 'utf-8-sig') as f:
            text = f.read()
        if text:
            self._browser.setText(text)

    def save_file(self):
        new_text = self._browser.toPlainText()
        if new_text and self.dict_file:
            with open(self.dict_file, "wt", encoding="utf-8-sig") as f:
                f.write(new_text)
                msg = "文件保存成功！"
                self.term_saving.emit(msg)
