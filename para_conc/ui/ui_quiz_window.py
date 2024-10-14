#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

from PySide6.QtWidgets import QMainWindow, QTextEdit, QLabel, QGridLayout, QVBoxLayout,QSpinBox,\
     QHBoxLayout, QPushButton, QGroupBox, QCheckBox, QLineEdit,QStatusBar, QComboBox, QRadioButton, QButtonGroup
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
import os, sys, re, random, json
from PySide6.QtWidgets import QApplication
from collections import defaultdict

class QuizWindow(QMainWindow):
    get_corpus = Signal(str)
    def __init__(self, parent=None):
        super(QuizWindow, self).__init__(parent)
        self.setWindowTitle('抽取翻译习题')
        self.setFixedSize(500, 500)
        currentDir = os.getcwd()
        self.setWindowIcon(QIcon(currentDir + "/app_data/images/vquote.png"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setIconSize(QSize(100, 40))
        self._statusBar = QStatusBar()
        self.setStatusBar(self._statusBar)        
        workDir = os.path.join(currentDir, "app_data","workfiles")
        self.saveDir = os.path.join(currentDir,"saved_files")
        self._header_img = os.path.join(currentDir, "app_data","images", 'trans_title.png')
        
        max_width = 460
        max_height = 500
        
        self._current_corpus = ""
        self._text_corpus = ""
        self._current_file_id = ""
        self._current_quiz_text =""
        self._current_ref_text = ""
        self._quiz_result = ""
       
        self._main_frame= QLabel()
        self._main_frame_layout = QVBoxLayout()       

        self._header_label = QLabel()
        self._header_label.setFixedWidth(400)
        self._header_label.setFixedHeight(80)
        self._header_label.setStyleSheet("QLabel{border-image: url(./app_data/images/trans_title.png);}")
        
        self._corp_title = QLabel("当前语料中文标题:")
        self._corp_title_box = QLineEdit()
        self._corp_title_box.setReadOnly(True)
        
        self._corp_info_layout = QGridLayout()
        self._corp_info_layout.addWidget(self._corp_title, 0, 0)
        self._corp_info_layout.addWidget(self._corp_title_box, 0, 1)

        self._quiz_setting = QGroupBox("抽取设置")
        self._quiz_setting_layout = QGridLayout()

        self._lang_label = QLabel("翻译方向:")
        self._lang_btns = QButtonGroup()        
        self._trans_to_en = QRadioButton("汉译英")
        self._trans_to_zh = QRadioButton("英译汉")
        self._trans_to_en.setChecked(True)
        self._lang_btns.addButton(self._trans_to_en)
        self._lang_btns.addButton(self._trans_to_zh)
       
        self._unit_label = QLabel("翻译单位:")
        self._unit_btns = QButtonGroup()
        self._trans_para = QRadioButton("单个段落")
        self._trans_sent = QRadioButton("单个句子")
        self._trans_para.setChecked(True)
        self._unit_btns.addButton(self._trans_para)
        self._unit_btns.addButton(self._trans_sent)
        self._ref_box = QCheckBox("参考译文")
        self._ref_box.setChecked(True)
        
        self._quiz_num_label = QLabel("翻译题数:")
        self._quiz_num_label.setFixedWidth(80)
        self._quiz_num = QSpinBox()
        self._quiz_num.setRange(1,10)
        self._quiz_num.setValue(5)
        self._quiz_num.setFixedWidth(40)
        
        self._quiz_setting_layout.addWidget(self._lang_label,0,0)
        self._quiz_setting_layout.addWidget(self._trans_to_en,0,1)
        self._quiz_setting_layout.addWidget(self._trans_to_zh,0,2)
        self._quiz_setting_layout.addWidget(self._ref_box,0,3,1,2)
        self._quiz_setting_layout.addWidget(self._unit_label,1,0)
        self._quiz_setting_layout.addWidget(self._trans_para,1,1)
        self._quiz_setting_layout.addWidget(self._trans_sent,1,2)        
        self._quiz_setting_layout.addWidget(self._quiz_num_label,1,3)
        self._quiz_setting_layout.addWidget(self._quiz_num,1,4)
        
        self._quiz_setting.setLayout(self._quiz_setting_layout)
        
        self._show_frame= QGroupBox("抽取结果", alignment=Qt.AlignCenter)
        self._show_frame_layout = QVBoxLayout()
        self._quiz_window = QTextEdit()
        self._quiz_window.setFixedWidth(max_width)
        self._quiz_window.setReadOnly(True)
        
        self._show_frame_layout.addWidget(self._quiz_window, alignment=Qt.AlignCenter|Qt.AlignTop)
        self._show_frame.setLayout(self._show_frame_layout)
        
        btn_max = 100
        btn_min = 80

        self._btn_layout = QHBoxLayout()
       
        self._get_quote_btn = QPushButton("开始抽取")        
        self._get_quote_btn.setFixedWidth(btn_min)
        self._get_quote_btn.clicked[bool].connect(self.get_quiz_data)
        self._quit_btn = QPushButton("关闭退出")        
        self._quit_btn.clicked[bool].connect(self.close)
        self._quit_btn.setFixedWidth(btn_min)
        self._save_btn = QPushButton("保存结果")
        self._save_btn.clicked[bool].connect(self.save_data)
        self._save_btn.setFixedWidth(btn_min)
        self._btn_layout.addWidget(self._get_quote_btn)
        self._btn_layout.addWidget(self._save_btn)
        self._btn_layout.addWidget(self._quit_btn)

        self._main_frame_layout.addWidget(self._header_label, alignment=Qt.AlignTop|Qt.AlignCenter)
        self._main_frame_layout.addStretch(1)
        self._main_frame_layout.addLayout(self._corp_info_layout)
        self._main_frame_layout.addStretch(1)
        self._main_frame_layout.addWidget(self._quiz_setting)
        self._main_frame_layout.addStretch(1)
        self._main_frame_layout.addWidget(self._show_frame, alignment=Qt.AlignTop)
        self._main_frame_layout.addStretch(6)
        self._main_frame_layout.addLayout(self._btn_layout)
        self._main_frame_layout.addStretch(0)
        
        self._main_frame.setLayout(self._main_frame_layout)
        self.setCentralWidget(self._main_frame)
        
    def get_setting(self):
        quiz_dict = {}
        quiz_dict['lang'] = "en"
        quiz_dict['unit'] = 'para'
        quiz_dict['ref'] = 'off'
        quiz_dict['num'] = self._quiz_num.value()
        if self._trans_to_en.isChecked():
            quiz_dict['lang'] = "zh"
        if self._trans_sent.isChecked():
            quiz_dict['unit'] = 'sent'
        if self._ref_box.isChecked():
            quiz_dict['ref'] = 'on'
        return quiz_dict
            
    def get_quiz_data(self):
        self._quiz_window.clear()
        self._current_quiz_text = ""
        self._current_ref_text = ""
        self._quiz_result = ""
        quiz_settings = self.get_setting()
        self.get_corpus.emit('get_corpus')
        if self._current_corpus:
            if self._current_corpus[1]:
                self._text_corpus = self._current_corpus[1]
            else:
                self._text_corpus = self._current_corpus[0]
            if quiz_settings['unit'] == 'para':
                para_scope = []
                for para in self._text_corpus.paras:
                     if para.raw_text_zh and para.raw_text_en:
                         if para.raw_text_en != '[UnTr]':
                             para_scope.append((para.raw_text_zh,para.raw_text_en.replace("[PS]","")))                         
                candidate = random.sample(para_scope, quiz_settings['num'])
                candidate_qlist = [x for (x, y) in candidate]
                candidate_klist = [y for (x, y) in candidate]
                if quiz_settings['lang'] == 'zh':
                    q_lead = "※ 请将下列中文段落译成英文："
                    k_lead = "※ 参考译文："
                    q_list = [f"{i}. {para}" for i, para in enumerate(candidate_qlist,start = 1)]
                    k_list = [f"{j}. {para}" for j, para in enumerate(candidate_klist,start = 1)]
                    self._current_quiz_text = q_lead+"\n"+"\n".join(q_list)
                    self._current_ref_text = k_lead+"\n"+"\n".join(k_list)                   
                else:
                    q_lead = "※ Please translate the following paragraphs into Chinese:"
                    k_lead = "※ Translation for reference:"
                    q_list = [f"{i}. {para}" for i, para in enumerate(candidate_klist,start = 1)]
                    k_list = [f"{j}. {para}" for j, para in enumerate(candidate_qlist,start = 1)]
                    self._current_quiz_text = q_lead+"\n"+"\n".join(q_list)
                    self._current_ref_text = k_lead+"\n"+"\n".join(k_list)
                if quiz_settings['ref'] == 'on':
                    self._quiz_window.setText(self._current_quiz_text+"\n"+self._current_ref_text)
                else:
                    self._quiz_window.setText(self._current_quiz_text)
                self.set_status_text("翻译测试题已抽取。")
            else:
                sent_scope = []
                for para in self._text_corpus.paras:
                    for sent in para.sents:
                        if sent.zh and sent.en:
                            if sent.en != '[UnTr]':
                                sent_scope.append((sent.zh,sent.en.replace("[PS]","")))
                candidate = random.sample(sent_scope, quiz_settings['num'])
                candidate_qlist = [x for (x, y) in candidate]
                candidate_klist = [y for (x, y) in candidate]
                if quiz_settings['lang'] == 'zh':
                    q_lead = "※ 请将下列中文句子译成英文："
                    k_lead = "※ 参考译文："
                    q_list = [f"{i}. {sent}" for i, sent in enumerate(candidate_qlist,start = 1)]
                    k_list = [f"{j}. {sent}" for j, sent in enumerate(candidate_klist,start = 1)]
                    self._current_quiz_text = q_lead+"\n"+"\n".join(q_list)
                    self._current_ref_text = k_lead+"\n"+"\n".join(k_list)                   
                else:
                    q_lead = "※ Please translate the following sentences into Chinese:"
                    k_lead = "※ Translation for reference:"
                    q_list = [f"{i}. {sent}" for i, sent in enumerate(candidate_klist,start = 1)]
                    k_list = [f"{j}. {sent}" for j, sent in enumerate(candidate_qlist,start = 1)]
                    self._current_quiz_text = q_lead+"\n"+"\n".join(q_list)
                    self._current_ref_text = k_lead+"\n"+"\n".join(k_list)
                if quiz_settings['ref'] == 'on':
                    self._quiz_result = self._current_quiz_text+"\n"+self._current_ref_text
                    
                else:
                    self._quiz_result = self._current_quiz_text
                self._quiz_window.setText(self._quiz_result)
                self._current_file_id = self._corp_title_box.text().replace(" ","").replace("\n","")
                self.set_status_text("翻译测试题已抽取。")
                
        else:
            self.set_status_text("待检索文件缺失，请先加载当前语料。")          
            
    def save_data(self):
        current_id = self._corp_title_box.text().replace(" ","").replace("\n","")
        if self._current_file_id and self._quiz_result:
            if current_id == self._current_file_id:
                fileToSave = os.path.join(self.saveDir, self._current_file_id+"_翻译习题.txt")
                title = "翻译习题\n选自《"+self._current_file_id+"》"
                with open(fileToSave, "wt", encoding = "utf-8-sig") as f:
                    f.write(title+"\n"+self._quiz_result)
                    self.set_status_text("当前翻译习题已成功保存到本地！")
            else:
                self.set_status_text("当前翻译习题为空：请先抽取习题，再保存结果！")
        elif self._current_file_id:
            self.set_status_text("抱歉，请先抽取抽取习题！")
        elif self._quiz_result:
            self.set_status_text("抱歉，请先加载当前语料！")
        else:
            self.set_status_text("抱歉，请先加载当前语料！")
    
    def set_status_text(self, text):
        self._statusBar.showMessage(text, 3000) 
