#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import os, sys, copy, pickle, time, re

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QAction, QPixmap, QTextOption
from PySide6.QtWidgets import (QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QComboBox,QTabWidget,
                             QGroupBox, QPushButton, QLineEdit, QLabel, QRadioButton, QStatusBar,
                             QButtonGroup, QTextBrowser, QCompleter, QProgressBar, QApplication,
                             QCheckBox, QAbstractItemView, QWidget, QMessageBox, QSplitter, 
                             QTreeWidgetItem, QTreeWidget)

from para_conc.core.thread_elm_obtainer import ElmObtainerThread
from para_conc.core.lg_dict import LG_DICT

class TextbookWindow(QMainWindow):
    def __init__(self, parent=None):
        super(TextbookWindow, self).__init__(parent)        
        currentDir = os.getcwd()
        dataDir = os.path.join(currentDir, "app_data")
        self.saveDir= os.path.join(currentDir, "saved_files")
        self.textBookDir = os.path.join(dataDir, "textbooks")
        workFileDir = os.path.join(dataDir, "workfiles")        
        self.imgDir = os.path.join(dataDir, "images")        
        self.lgd = LG_DICT['2']
        self.font = QFont("Times New Man",12)
        
        self.error = ""                                
        self.en_text_data = []
        self.current_text = ""
        self.current_elements = ""        
        self._corpus_selected_list = []
        
        self._left_frame_layout = QVBoxLayout()
        self._corpusFrame = QGroupBox('语料列表')
        self._corpusFrame.setToolTip('双击文件名打开当前语料，按Shift或Ctrol键点选多个语料')
        self._corpusFrameLayout = QVBoxLayout()
        
        self._optionFrame = QGroupBox()
        self._optionFrame_layout = QGridLayout()
        self._get_element_btn = QPushButton("提取元素")
        self._get_element_btn.setFixedWidth(80)
        self._get_element_btn.clicked.connect(self.get_element)
        self._save_element_btn = QPushButton("保存结果")
        self._save_element_btn.setFixedWidth(80)
        self._save_element_btn.clicked.connect(self.save_element)
        self._optionFrame_layout.addWidget(self._get_element_btn,0,0)
        self._optionFrame_layout.addWidget(self._save_element_btn,0,1)
        self._optionFrame.setLayout(self._optionFrame_layout)

        self._pg_bar = QProgressBar(self)
        self._pg_bar.setFixedWidth(150)
        self._pg_bar.setFixedHeight(20)
        self._pg_bar.setRange(0, 5)
        self._pg_bar.setFormat("%v/%m")
        self._pg_bar.setValue(0)  
        
        self._left_frame_layout.addWidget(self._corpusFrame)
        self._left_frame_layout.addWidget(self._optionFrame)
        self._left_frame_layout.addWidget(self._pg_bar) 

        self._tabWidget= QTabWidget()
        self._tabWidget.setMaximumHeight(500)
        self._tabWidget.setMaximumWidth(550)

        self._text_window = QTextBrowser(parent)
        self._text_window.setFrameStyle(0)
        self._elem_window = QTextBrowser(parent)
        self._elem_window.setFrameStyle(0)

        self._tabWidget.addTab(self._text_window,"课文内容")
        self._tabWidget.addTab(self._elem_window,"提取结果")

        self._right_frame_layout = QVBoxLayout()
        self._right_frame_layout.addWidget(self._tabWidget)

        mainWidget = QWidget()
        mainLayout = QHBoxLayout(mainWidget)
        mainLayout.setSpacing(2)
        mainLayout.addLayout(self._left_frame_layout, 0)
        mainLayout.addLayout(self._right_frame_layout, 1)
        self.setCentralWidget(mainWidget)

        self._statusBar = QStatusBar()
        self._statusBar.showMessage('欢迎使用 外语教材自定义语料库')
        self.setStatusBar(self._statusBar)

        self.setFixedSize(700, 500)
        self.setObjectName("MainWindow")
        self.setWindowTitle("外语教材自定义语料库")
        
        self.setWindowIcon(QIcon(currentDir + "/app_data/workfiles/myIcon.png"))
        self.setIconSize(QSize(100, 40))
        
        self.data_preload()
   
    def data_preload(self):
        self._corpusWindow = QTreeWidget()
        #self._corpusWindow.setStyleSheet("QTreeWidget{background-color:%s}"% ("WhiteSmoke"))
        self._corpusWindow.setStyleSheet("QTreeWidget{border-image: url(./app_data/images/lide.png);background-color:%s}"% ("WhiteSmoke"))
        self._corpusWindow.setFixedWidth(200)
        self._corpusWindow.setMaximumWidth(200)
        self._corpusWindow.setFixedHeight(400)
        self._corpusWindow.setSortingEnabled(False)        
        self._corpusWindow.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._corpusWindow.setColumnCount(1)
        self._corpusWindow.itemDoubleClicked.connect(self.openCurrentFileRequest)        
        self._corpusWindow.itemSelectionChanged.connect(self.selecting_item)
        self._corpusWindow.setContextMenuPolicy(Qt.CustomContextMenu)
        self._corpusWindow.setHeaderHidden(True)

        self._tabWidget.setTabText(1,"AI提取结果")

        root_list = []
        for data_dir in os.listdir(self.textBookDir):
            root = QTreeWidgetItem()
            root.setText(0,data_dir)
            root_list.append(root)
            data_directory = os.path.join(self.textBookDir,data_dir)
            list_data = os.listdir(data_directory)
            list_sorted = self.list_sorter(list_data)
            for data in list_sorted:
                if data.endswith(".txt"):
                    user_data = os.path.join(data_directory,data)
                    self.en_text_data.append(user_data)
                    show_item = data.split('\\')[-1].replace(".txt","")                    
                    child = QTreeWidgetItem()
                    child.setText(0,show_item)
                    root.addChild(child)
                    root_list.append(child)
        if root_list:
            self._corpusWindow.insertTopLevelItems(0,root_list)
            self._corpusFrameLayout.addWidget(self._corpusWindow, alignment=Qt.AlignTop)
            self._corpusFrame.setLayout(self._corpusFrameLayout)
        self._corpusFrame.setTitle(f"语料列表（{len(self.en_text_data)}）")
        
    def list_sorter(self, target):
        my_list = []
        patterna = re.compile(r'([a-zA-Z]+)([0-9]+)([a-zA-Z]+)([0-9]+)([a-zA-Z]+)([0-9]+)')
        patternb = re.compile(r'([a-zA-Z]+)([0-9]+)([a-zA-Z]+)([0-9]+)')
        patternc = re.compile(r'([a-zA-Z]+)([0-9]+)')
        try:
            my_list = sorted(target, key=lambda x: (patterna.match(x.split("_")[1]).groups()[0], int(patterna.match(x.split("_")[1]).groups()[1]),\
                                             patterna.match(x.split("_")[1]).groups()[2], int(patterna.match(x.split("_")[1]).groups()[3]),\
                                             patterna.match(x.split("_")[1]).groups()[4], int(patterna.match(x.split("_")[1]).groups()[5])))
        except:
            my_list = []
        if not my_list:
            try:
                my_list = sorted(target, key=lambda x: (patternb.match(x.split("_")[1]).groups()[0], int(patternb.match(x.split("_")[1]).groups()[1]),\
                                             patternb.match(x.split("_")[1]).groups()[2], int(patternb.match(x.split("_")[1]).groups()[3])))
            except:
                my_list = []
        if not my_list:
            try:
                my_list = sorted(target, key=lambda x: (patternc.match(x.split("_")[1]).groups()[0], int(patternc.match(x.split("_")[1]).groups()[1])))
            except:
                my_list = target
        return my_list               
        

    def flash_message(self, msg):
        self._statusBar.showMessage(msg,8000)

    def thread_run(self, request, key):
        self.getter = ElmObtainerThread(request, key)
        self.getter.finished.connect(self.getter.deleteLater)
        self.getter.pbar_signal.connect(self.update_pbar)
        self.getter.msg_m_signal.connect(self.flash_message)
        self.getter.output_signal.connect(self.update_content) 
        self.getter.start()
        
    def update_content(self,m,n):
        self.result = m
        self.error = n
        if self.result:
            self.current_elements = self.result.replace("\n\n",'\n')
            self._elem_window.clear()
            self._elem_window.setText(self.current_elements)
            self._tabWidget.setCurrentIndex(1) 
        else:
            if self.error:
                self.flash_message(f"抱歉，思政元素提取失败，错误代码：{self.error}")
            else:
                self.flash_message("抱歉，思政元素提取失败，请检查网络是否畅通")

    def update_pbar(self, i,j):
        self._pg_bar.setVisible(True)
        self._pg_bar.setFormat("%v%")
        k = int(i/j*100)
        self._pg_bar.setRange(0,100)
        if i != -1:
            self._pg_bar.setValue(k)
            time.sleep(0.1)
        else:
            self._pg_bar.setValue(0)                
               
    def get_element(self):
        if self.current_text:            
            question_stem = "你是一个思政元素提取专家，你的任务是从以下英文中为用户提供专业、准确的思政元素，回复时请用中文：\n"
            element_request = question_stem + self.current_text[1].replace("\n\n","\n")
            self.thread_run(element_request, self.lgd)
        else:
            self.flash_message("请先单击语料列表中的某篇文章")
        
    def selecting_item(self):
        self._corpus_selected_list.clear()
        for item in self._corpusWindow.selectedItems():
            if item.text(0) not in self._corpus_selected_list:
                self._corpus_selected_list.append(item.text(0))
                
    def listItemRightClicked(self):
        pass

    def save_element(self):
        if self.current_text and self.current_elements:
            file_to_save = os.path.join(self.saveDir, self.current_text[0]+'_elm.txt')
            with open (file_to_save, 'wt', encoding= "utf-8-sig") as f:
                f.write(self.current_elements)
            self.flash_message(f"{self.current_text[0]}的提取结果已保存！")
        else:
            self.flash_message(f"请先提取元素，再保存结果！")

    def openCurrentFileRequest(self, item):
        data_id = item.text(0)
        for data in self.en_text_data:
            if data_id in data:
                with open(data, 'rt', encoding = "utf-8-sig") as f:                    
                    text = f.read()
                    self._text_window.clear()
                    self._elem_window.clear()
                    self.current_elements = ""
                    self._text_window.setText(text)
                    self.current_text = (data_id, text)
                    self._tabWidget.setCurrentIndex(0)                    
                    break
                
    def resizeFontUp(self):
        if self.font.pointSize() >= 16:
            pass
        else:
            font_size = self.font.pointSize()+1
            font_family = self.font.family()
            self.font = QFont(font_family, font_size)
            self._text_window.setFont(self.font)
            self._elem_window.setFont(self.font)
    
    def resizeFontDown(self):
        if self.font.pointSize() <= 8:
            pass
        else:
            font_size = self.font.pointSize()-1
            font_family = self.font.family()
            self.font = QFont(font_family, font_size)
            self._text_window.setFont(self.font)
            self._elem_window.setFont(self.font)
        
    def keyReleaseEvent(self, event):
        modifiers = event.modifiers()
        if modifiers == (Qt.ControlModifier) and event.key()==Qt.Key_Up:
            self.resizeFontUp()
        if modifiers == (Qt.ControlModifier) and event.key()==Qt.Key_Down:
            self.resizeFontDown()
