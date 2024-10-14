#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

from PySide6.QtWidgets import QMainWindow, QTextEdit, QLabel, QGridLayout, QHBoxLayout, \
     QVBoxLayout, QPushButton, QGroupBox, QCheckBox, QLineEdit, QComboBox, QRadioButton, \
     QSpinBox, QTextBrowser
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PIL import Image, ImageQt

class WordCloudWindow(QMainWindow):
    error_input_warning = Signal(str)
    filter_dict_output = Signal(dict)
    picture_show_request = Signal(str)    
    def __init__(self, parent=None):
        super(WordCloudWindow, self).__init__(parent)
        self._filter_choices = {}        
        self._color_dict ={"透明":None,"黑色":"black", "红色":"red", "蓝色":"blue",\
                           "绿色":"green", "黄色":"yellow", "紫色":"purple", \
                           "灰色":"gray", "白色":"white", "自动":None}
        
        self.setWindowTitle('词云设置')
        self.setGeometry(300, 100, 620, 200)
        self.setFixedSize(600, 260)
        self._browser= QGroupBox()
        self._browser_layout = QVBoxLayout()

        self._option_lang = QGroupBox()
        self._option_lang_layout = QGridLayout()
        self._lang_label = QLabel("词云类型")
        self._lang_zh = QRadioButton("中文词云")
        self._lang_en = QRadioButton("英文词云")
        self._lang_bi = QRadioButton("双语词云")
        self._lang_zh.setChecked(True)
        self._option_lang_layout.addWidget(self._lang_label, 0,0)
        self._option_lang_layout.addWidget(self._lang_zh, 0,1)
        self._option_lang_layout.addWidget(self._lang_en, 0,2)
        self._option_lang_layout.addWidget(self._lang_bi, 0,3)
        self._option_lang.setLayout(self._option_lang_layout)
        
        self._option_scope = QGroupBox()
        self._option_scope_layout = QGridLayout()
        self._scope_label = QLabel("词云范围")
        self._scope_default = QRadioButton("当前语料")
        self._scope_selected = QRadioButton("所选语料")
        self._scope_all = QRadioButton("全部语料")        
        self._scope_default.setChecked(True)
        self._option_scope_layout.addWidget(self._scope_label, 1,0)
        self._option_scope_layout.addWidget(self._scope_default, 1,1)
        self._option_scope_layout.addWidget(self._scope_selected, 1,2)
        self._option_scope_layout.addWidget(self._scope_all, 1,3)
        self._option_scope.setLayout(self._option_scope_layout)        
        
        self._option_set = QGroupBox()
        self._option_set_layout = QVBoxLayout()
        
        self._option_tag_layout = QGridLayout()
        self._stoptag_check = QCheckBox()
        self._stoptag_check.setChecked(True)
        self._stoptag_label = QLabel("停用词性")
        self._stoptag_box = QTextEdit("C;D;I;L;M;P;S;T;U;W;X;.;,;:;(;);$;``;'';c;e;h;k;m;q;p;r;s;t;u;w;x;y")        
        self._stoptag_box.setFixedHeight(30)        
        self._stopword_check = QCheckBox()
        self._stopword_label = QLabel("停用词表")
        self._option_tag_layout.addWidget(self._stoptag_check, 0,0)
        self._option_tag_layout.addWidget(self._stoptag_label, 0,1)
        self._option_tag_layout.addWidget(self._stoptag_box, 0,2)
        self._option_tag_layout.addWidget(self._stopword_check, 0,3)
        self._option_tag_layout.addWidget(self._stopword_label, 0,4)

        self._option_word_layout = QGridLayout()
        
        self._fontmax_label = QLabel("最大字号")
        self._fontmax_label.setFixedWidth(60)
        self._fontmax_box = QLineEdit("自动")
        self._fontmax_box.setFixedWidth(50)
        self._fontmin_label = QLabel("最小字号")
        self._fontmin_label.setFixedWidth(60)
        self._fontmin_box = QLineEdit("4")
        self._fontmin_box.setFixedWidth(50)
        self._wordmax_label = QLabel("最多词数")
        self._wordmax_label.setFixedWidth(60)
        self._wordmax_box = QLineEdit("1000")
        self._wordmax_box.setFixedWidth(50)
        self._stoplength_label = QLabel("最小词长")
        self._stoplength_label.setFixedWidth(60)
        self._stoplength_box = QLineEdit("2")
        self._stoplength_box.setFixedWidth(50)
        self._stopfreq_label = QLabel("最小词频")
        self._stopfreq_label.setFixedWidth(60)
        self._stopfreq_box = QLineEdit("2")
        self._stopfreq_box.setFixedWidth(50)
        
        self._option_word_layout.addWidget(self._stoplength_label, 0,2)
        self._option_word_layout.addWidget(self._stoplength_box, 0,3)
        self._option_word_layout.addWidget(self._stopfreq_label, 0,4)
        self._option_word_layout.addWidget(self._stopfreq_box, 0,5)
        self._option_word_layout.addWidget(self._fontmin_label, 0,6)
        self._option_word_layout.addWidget(self._fontmin_box, 0,7)
        self._option_word_layout.addWidget(self._fontmax_label, 0,8)
        self._option_word_layout.addWidget(self._fontmax_box, 0,9)
        self._option_word_layout.addWidget(self._wordmax_label, 0,10)
        self._option_word_layout.addWidget(self._wordmax_box, 0,11)

        self.color_list = ["透明","黑色","红色","蓝色","绿色","黄色","紫色","灰色","白色"]
        self._option_color_layout = QGridLayout()
        self._mode_label = QLabel("颜色模式")
        self._mode_label.setFixedWidth(60)
        self._mode_box = QLineEdit("RGBA")
        self._mode_box.setFixedWidth(50)
        self._wordcolor_label = QLabel("文字颜色")
        self._wordcolor_label.setFixedWidth(60)
        self._wordcolor_box = QComboBox()
        self._wordcolor_box.setFixedWidth(50)
        for color_id in self.color_list:
            if color_id == "透明":
                self._wordcolor_box.addItem("自动")
            else:
                self._wordcolor_box.addItem(color_id)
        self._random_label = QLabel("随机色数")
        self._random_label.setFixedWidth(60)
        self._random_box = QLineEdit("20")
        self._random_box.setFixedWidth(50)
        self._groundcolor_label = QLabel("背景颜色")
        self._groundcolor_label.setFixedWidth(60)
        self._groundcolor_box = QComboBox()
        self._groundcolor_box.setFixedWidth(50)
        for color_id in self.color_list:
            self._groundcolor_box.addItem(color_id)       
        self._mask_button = QCheckBox("蒙板")
        self._mask_button.setFixedWidth(70)
        self._mask_button.setChecked(True)
        self._mask_id = QSpinBox()
        self._mask_id.setRange(1,120)
        self._mask_id.setValue(85)
        self._mask_id.setFixedWidth(50)
        self._option_color_layout.addWidget(self._mode_label, 0,0)
        self._option_color_layout.addWidget(self._mode_box, 0,1)
        self._option_color_layout.addWidget(self._wordcolor_label, 0,2)
        self._option_color_layout.addWidget(self._wordcolor_box, 0,3)
        self._option_color_layout.addWidget(self._groundcolor_label, 0,4)
        self._option_color_layout.addWidget(self._groundcolor_box, 0,5)
        self._option_color_layout.addWidget(self._random_label, 0,6)
        self._option_color_layout.addWidget(self._random_box, 0,7)        
        self._option_color_layout.addWidget(self._mask_button, 0,8)
        self._option_color_layout.addWidget(self._mask_id, 0,9)
        self._option_set_layout.addLayout(self._option_tag_layout)
        self._option_set_layout.addLayout(self._option_word_layout)
        self._option_set_layout.addLayout(self._option_color_layout)

        self._option_set.setLayout(self._option_set_layout)
        
        self._ok_button = QPushButton("开始绘制")
        self._ok_button.setFixedWidth(80)
        self._ok_button.clicked[bool].connect(self.generate_wordcloud_request)        
               
        self._browser_layout.addWidget(self._option_lang, alignment=Qt.AlignTop)
        self._browser_layout.addWidget(self._option_scope, alignment=Qt.AlignTop)
        self._browser_layout.addWidget(self._option_set,alignment=Qt.AlignTop)
        self._browser_layout.addWidget(self._ok_button,alignment=Qt.AlignBottom|Qt.AlignCenter)
        self._browser.setLayout(self._browser_layout)
        self.setCentralWidget(self._browser)
        self.setWindowIcon(QIcon("./app_data/images/cloud.png"))

    def get_filter_options(self):
        warning = []
        filter_dict = {}
        filter_dict['lang'] = 'zh'
        if self._lang_en.isChecked():
            filter_dict['lang'] = 'en'
        if self._lang_bi.isChecked():
            filter_dict['lang'] = 'bi'
        filter_dict['scope'] = 'current'
        if self._scope_selected.isChecked():
            filter_dict['scope'] = 'selected'
        if self._scope_all.isChecked():
            filter_dict['scope'] = 'all'        
        filter_dict['stop_list'] = "off"
        if self._stopword_check.isChecked():
            filter_dict['stop_list'] = "on"
        try:
            filter_dict['length']=int(self._stoplength_box.text())
        except:
            warning.append("最小词长输入错误，请重试！")
            filter_dict['length']=2
        try:
            filter_dict['freq']= int(self._stopfreq_box.text())
        except:
            warning.append("最小词频输入错误，请重试！")
            filter_dict['freq']= 2
        try:
            filter_dict['font_min']= int(self._fontmin_box.text())
        except:
            warning.append("最小字号输入错误，请重试！")
            filter_dict['font_max']= 4
        try:
            filter_dict['font_max']= int(self._fontmax_box.text())
        except:
            filter_dict['font_max']= None
        try:
            filter_dict['word_max']= int(self._wordmax_box.text())
        except:
            filter_dict['word_max']= 1000
        filter_dict['mode']= "RGBA"
        if self._mode_box.text() != "RGBA":
            filter_dict['mode'] = "RGB"
        try:
            filter_dict['random']= int(self._random_box.text())
        except:
            filter_dict['random']= 20
        filter_dict['tag']=[]
        if self._stoptag_check.isChecked():
            filter_dict['tag']= self._stoptag_box.toPlainText().split(';')
        color_bg_id = self._groundcolor_box.currentText()
        filter_dict['bg_color']= self._color_dict[color_bg_id]
        color_wd_id = self._wordcolor_box.currentText()
        filter_dict['wd_color']= self._color_dict[color_wd_id]
        filter_dict['mask'] = None    
        if self._mask_button.isChecked():
            filter_dict['mask'] = str(self._mask_id.value())
        return filter_dict, warning
    
    def generate_wordcloud_request(self):        
        filter_dict, warning_list = self.get_filter_options()
        if warning_list:
            self.error_input_warning.emit(";".join(warning_list))            
        else:
            self.filter_dict_output.emit(filter_dict)
            self.picture_show_request.emit("show")
        self.close()

class WordCloudShowWindow(QMainWindow):
    picture_save_request = Signal(str)
    def __init__(self, parent=None):
        super(WordCloudShowWindow, self).__init__(parent)
        self._filter_choices = {}
        self.setWindowTitle('词云展示')
        self.setGeometry(300, 200, 500, 500)
        self.setFixedSize(500, 500)
        self._browser= QGroupBox()
        self._browser_layout = QVBoxLayout()
        
        self._cloud_frame = QGroupBox()
        self._cloud_frame.setFixedHeight(450)
        self._cloud_frame_layout = QHBoxLayout()
        self._cloud_canvas = QLabel()
        self._cloud_canvas.setFixedWidth(450)
        self._cloud_frame_layout.addWidget(self._cloud_canvas, alignment = Qt.AlignCenter)
        self._cloud_frame.setLayout(self._cloud_frame_layout)
 
        self._option_frame_layout = QHBoxLayout()
        self._save_button = QPushButton("保存词云")
        self._save_button.setStatusTip('将当前显示的词云图片存贮到saved_files文件夹内')
        self._save_button.setFixedWidth(80)
        self._save_button.clicked[bool].connect(self.save_cloud)
        self._close_button = QPushButton("关闭词云")
        self._close_button.setFixedWidth(80)
        self._close_button.clicked[bool].connect(self.close)
        self._option_frame_layout.addWidget(self._save_button, alignment = Qt.AlignCenter)
        self._option_frame_layout.addWidget(self._close_button, alignment = Qt.AlignCenter)
        
        self._browser_layout.addWidget(self._cloud_frame, alignment = Qt.AlignCenter)
        self._browser_layout.addLayout(self._option_frame_layout)
        self._browser.setLayout(self._browser_layout)
        self.setCentralWidget(self._browser)
        self.setWindowIcon(QIcon("./app_data/images/cloud.png"))

    def update_canvas(self, img):
        qimage = ImageQt.toqimage(img)
        qpixmap = ImageQt.toqpixmap(img)
        self._cloud_canvas.clear()
        self._cloud_canvas.setPixmap(qpixmap)
        self._cloud_canvas.setScaledContents (True)
        
    def save_cloud(self):
        self.picture_save_request.emit("save")
