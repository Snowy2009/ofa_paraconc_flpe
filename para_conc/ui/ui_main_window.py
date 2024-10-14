#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import os, sys, copy, pickle

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QAction, QPixmap, QBrush, QColor,QTextOption
from PySide6.QtWidgets import (QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QComboBox,
                             QGroupBox, QPushButton, QLineEdit, QLabel, QRadioButton, QStatusBar,
                             QButtonGroup, QTextBrowser, QCompleter, QProgressBar, 
                             QCheckBox, QWidget, QListWidget, QMessageBox, QSplitter,
                             QAbstractItemView,QTreeWidgetItem,QTreeWidget)

from para_conc.core.search.search import SearchMode, SearchScope
from para_conc.core.para_conc import ParaConc

class UIMainWindow(QMainWindow):    
    save_text = Signal()
    save_html = Signal()
    search = Signal()
    print_result = Signal()
    load_corpus = Signal(str)
    load_tag_corpus = Signal(str)
    textbook_window_display = Signal()
    zh_freq_output = Signal()
    en_freq_output = Signal()
    pynlpir_output = Signal()
    regex_output = Signal()
    cplist_output = Signal()
    code_output = Signal()
    penn_output = Signal()
    wordcloud_output = Signal()
    freqcount_output = Signal()
    quote_display = Signal()
    quiz_display = Signal()
    qdict_update = Signal()
    stop_zh_dict_update = Signal()
    stop_en_dict_update = Signal()
    bi_term_dict_update = Signal()
    set_freq = Signal()
    selecting_item = Signal()
    view_chapter = Signal(str, int)
    update_current_corpus = Signal(str)

    def __init__(self, parent=None):
        super(UIMainWindow, self).__init__(parent)        
        self.font = QFont("Times New Man",12)
        self._para_conc = ParaConc()
        self._word_dict = copy.deepcopy(self._para_conc.bi_dict)
        self._prompt_list = []
        for k, v_list in  self._word_dict.items():
            self._prompt_list.append(k)
            self._prompt_list.extend(v_list)
        currentDir = os.getcwd()
        dataDir = os.path.join(currentDir, "app_data")
        workFileDir = os.path.join(dataDir, "workfiles")        
        self.imgDir = os.path.join(dataDir, "images")
        self._outPutDir = os.path.join(currentDir, "saved_files")
        self._starter_page_img = os.path.join(self.imgDir, 'frontPageDefault.png')
        self._text_page_img = os.path.join(self.imgDir, 'rd_bg.png')

        aboutAction = QAction(QIcon('./app_data/images/about.png'),'&关于本软件', self)
        aboutAction.triggered.connect(self._info)        
        aboutAction.setStatusTip('查看软件制作信息')        
        pynlpirAction = QAction(QIcon('./app_data/images/zh.png'),'&中文词性赋码表', self)
        pynlpirAction.triggered.connect(self.pynlpir_output)
        pynlpirAction.setStatusTip('查看PYNLPIR中文词性赋码表')
        pennAction = QAction(QIcon('./app_data/images/en.png'),'&英文词性赋码表', self)
        pennAction.triggered.connect(self.penn_output)
        pennAction.setStatusTip('查看NLTK英文单词及词频')
        errorAction = QAction(QIcon('./app_data/images/dictc.png'),'&错误代码', self)
        errorAction.triggered.connect(self.code_output)
        errorAction.setStatusTip('查看AI提取错误代码')
        regexAction = QAction(QIcon('./app_data/images/stas.png'),'&正则表达式', self)
        regexAction.triggered.connect(self.regex_output)
        regexAction.setStatusTip('查看正则表达式符号释义')
        cplistAction = QAction(QIcon('./app_data/images/stas.png'),'&内嵌语料库列表', self)
        cplistAction.triggered.connect(self.cplist_output)
        cplistAction.setStatusTip('查看内嵌语料库列表')
        
        wordCloudAction = QAction(QIcon('./app_data/images/cloud.png'),'&生成词云', self)
        wordCloudAction.triggered.connect(self.wordcloud_output)
        wordCloudAction.setStatusTip('依据词频生成当前语料的词云')
        quoteAction = QAction(QIcon('./app_data/images/vquote.png'),'&抽取引言语料', self)
        quoteAction.triggered.connect(self.quote_display)
        quoteAction.setStatusTip('从当前语料中抽取引言双语数据')
        qdictAction = QAction(QIcon('./app_data/images/qdict.png'),'&更新引言词库', self)
        qdictAction.triggered.connect(self.qdict_update)
        qdictAction.setStatusTip('添加、修改或删除引言词库中的引言辞条')
        stopZhAction = QAction(QIcon('./app_data/images/dictc.png'),'&更新中文停用词表', self)
        stopZhAction.triggered.connect(self.stop_zh_dict_update)
        stopZhAction.setStatusTip('添加、修改或删除中文停用词表中的辞条') 
        stopEnAction = QAction(QIcon('./app_data/images/dicte.png'),'&更新英文停用词表', self)
        stopEnAction.triggered.connect(self.stop_en_dict_update)
        stopEnAction.setStatusTip('添加、修改或删除英文停用词表中的辞条')
        biTermAction = QAction(QIcon('./app_data/images/dictb.png'),'&更新双语术语词表', self)
        biTermAction.triggered.connect(self.bi_term_dict_update)
        biTermAction.setStatusTip('添加、修改或删除中英双语术语表中的辞条')          
      
        outTxtAction = QAction(QIcon('./app_data/images/txt.png'),'&输出检索结果到TXT文件', self)         
        outTxtAction.triggered.connect(self.save_text)
        outTxtAction.setStatusTip('将当前的检索结果输出为txt文件')
        outHtmlAction = QAction(QIcon('./app_data/images/html.png'),'&输出检索结果到HTML文件', self)
        outHtmlAction.triggered.connect(self.save_html)
        outHtmlAction.setStatusTip('将当前的检索结果输出为html文件')

        setTextSizeUpAction=QAction(QIcon('./app_data/images/up.png'),'&字号上调',self,triggered=self.resizeFontUp)
        setTextSizeUpAction.setShortcut('Ctrl+Up')
        setTextSizeDownAction=QAction(QIcon('./app_data/images/down.png'),'&字号下调',self,triggered=self.resizeFontDown)
        setTextSizeDownAction.setShortcut('Ctrl+Down')

        loadTextbookAction = QAction(QIcon('./app_data/images/qdict.png'),'&教材语料库', self)
        loadTextbookAction.triggered.connect(self.textbook_window_display)
        loadTextbookAction.setStatusTip('转入自定义教材语料库界面')
        
        exitAction = QAction(QIcon('./app_data/images/quit.ico'),'&退出', self)
        exitAction.triggered.connect(self.close)
        exitAction.setStatusTip('关闭退出')
        
        menubar = self.menuBar()
        menubar.setContextMenuPolicy(Qt.PreventContextMenu)
        
        fileMenu = menubar.addMenu("首页")
        fileMenu_subPage = fileMenu.addAction(loadTextbookAction)
        fileMenu_subPage = fileMenu.addAction(exitAction)
        
        toolMenu = menubar.addMenu('工具')
        toolMenu_fontGroup = toolMenu.addMenu(QIcon('./app_data/images/font.png'),'&字号调整')
        toolMenu_fontGroup.addAction(setTextSizeUpAction)
        toolMenu_fontGroup.addAction(setTextSizeDownAction)
        toolMenu_fixGroup = toolMenu.addMenu(QIcon('./app_data/images/fix.png'),'&语料维护')
        toolMenu_fixGroup.addAction(stopZhAction)
        toolMenu_fixGroup.addAction(stopEnAction)
        toolMenu_fixGroup.addAction(biTermAction)
        toolMenu_fixGroup.addAction(qdictAction)        
        toolMenu_saveGroup = toolMenu.addMenu(QIcon('./app_data/images/output.png'),'&语料输出')
        toolMenu_saveGroup.addAction(outTxtAction)
        toolMenu_saveGroup.addAction(outHtmlAction)
        
        helpMenu = menubar.addMenu('帮助')
        helpMenu_freqGroup = helpMenu.addMenu(QIcon('./app_data/images/pos.png'),'&词性赋码表')
        helpMenu_freqGroup.addAction(pynlpirAction)
        helpMenu_freqGroup.addAction(pennAction)
        helpMenu_code = helpMenu.addAction(errorAction)
        helpMenu_regex = helpMenu.addAction(regexAction)
        helpMenu_cplist = helpMenu.addAction(cplistAction)        
        
        infoMenu = menubar.addMenu('关于')
        infoMenu.addAction(aboutAction)

        self._left_frame_layout = QVBoxLayout()

        self._corpusFrame = QGroupBox('语料列表')        
        self._corpusFrame.setToolTip('双击文件名打开当前语料，按Shift或Ctrl键点选多个语料')
        self._corpusFrameLayout = QVBoxLayout()       

        self._optionFrame = QGroupBox('检索选项')
        self._optionFrame.setMaximumWidth(250)
        self._optionFrame_layout = QVBoxLayout()
        
        completer = QCompleter(self._prompt_list)
        
        self._input_layout = QHBoxLayout()
        self._input_box = QLineEdit()
        self._input_box.setFixedWidth(150)
        self._input_box.setCompleter(completer)
        self._input_button = QPushButton('检索')
        self._input_button.clicked.connect(self.search)
        self._input_button.setFixedWidth(80)
        self._input_layout.addWidget(self._input_box)
        self._input_layout.addWidget(self._input_button)

        self._src_scope = QButtonGroup()
        self._src_scope_list = QLabel("检索范围：")
        self._src_scope_1 = QRadioButton('全部语料')
        self._src_scope_1.setToolTip('检索语料列表内的所有语料')
        self._src_scope_2 = QRadioButton('所选语料')
        self._src_scope_2.setToolTip('检索语料列表内单选或多选的语料')
        self._src_scope_3 = QRadioButton('当前语料')
        self._src_scope_3.setToolTip('检索当前被激活的语料')
        self._src_scope_4 = QRadioButton('当前体裁')
        self._src_scope_4.setToolTip('检索与当前语料体裁相同的所有语料')
        self._src_scope.addButton(self._src_scope_1)
        self._src_scope.addButton(self._src_scope_2)
        self._src_scope.addButton(self._src_scope_3)
        self._src_scope.addButton(self._src_scope_4)
        self._src_scope_1.setChecked(True)
        self._src_scope.setExclusive(True)

        self._src_scope_layout = QGridLayout()
        self._src_scope_layout.addWidget(self._src_scope_list, 0, 0)
        self._src_scope_layout.addWidget(self._src_scope_1, 1, 0)
        self._src_scope_layout.addWidget(self._src_scope_2, 1, 1)
        self._src_scope_layout.addWidget(self._src_scope_3, 2, 0)
        self._src_scope_layout.addWidget(self._src_scope_4, 2, 1)
        
        self._src_mode = QButtonGroup()
        self._src_mode_list = QLabel('检索方式：')
        self._src_mode_1 = QRadioButton('普通检索')
        self._src_mode_1.setToolTip('按输入检索词原样进行精确搜索')
        self._src_mode_2 = QRadioButton('拓展检索')
        self._src_mode_2.setToolTip('对输入词汇进行词形还原、忽略大小写等多重模糊搜索')
        self._src_mode_2.setChecked(True)
        self._src_mode_3 = QRadioButton('正则检索')
        self._src_mode_3.setToolTip('根据输入的正则表达式进行模糊搜索')
        self._src_mode.addButton(self._src_mode_1)
        self._src_mode.addButton(self._src_mode_2)
        self._src_mode.addButton(self._src_mode_3)

        self._src_mode_layout = QGridLayout()
        self._src_mode_layout.addWidget(self._src_mode_list, 0, 0)
        self._src_mode_layout.addWidget(self._src_mode_1, 1, 0)
        self._src_mode_layout.addWidget(self._src_mode_2, 1, 1)
        self._src_mode_layout.addWidget(self._src_mode_3, 1, 2)

        self._dsp_mode_list = QLabel('展示方式：')
        self._dsp_context_button = QCheckBox('展示语境')
        self._dsp_context_button.setToolTip('同时展示检索句所在语段的具体内容')
        self._dsp_context_button.setChecked(False)
        self._dsp_source_button = QCheckBox('展示语源')
        self._dsp_source_button.setToolTip('同时展示检索句所在章节的具体信息')
        self._dsp_source_button.setChecked(False)
        self._dsp_note_button = QCheckBox('展示注释')
        self._dsp_note_button.setToolTip('同时展示检索句内所含注释项的具体信息')
        self._dsp_note_button.setChecked(False)       

        self._dsp_mode_layout = QGridLayout()
        self._dsp_mode_layout.addWidget(self._dsp_mode_list, 0, 0)        
        self._dsp_mode_layout.addWidget(self._dsp_source_button, 1, 0)
        self._dsp_mode_layout.addWidget(self._dsp_context_button, 1, 1)
        self._dsp_mode_layout.addWidget(self._dsp_note_button, 1, 2)
        
        self._statistic_win = QGroupBox("数据统计")
        self._words_hit_label = QLabel("关键词检索命中数：")
        self._words_hit_value = QLabel("0")
        self._pairs_hit_label = QLabel("句对组检索命中数：")
        self._pairs_hit_value = QLabel("0")
        self._statistic_layout= QGridLayout()
        self._statistic_layout.addWidget(self._words_hit_label, 0, 0)
        self._statistic_layout.addWidget(self._words_hit_value, 0, 1)
        self._statistic_layout.addWidget(self._pairs_hit_label, 1, 0)
        self._statistic_layout.addWidget(self._pairs_hit_value, 1, 1)
        self._statistic_win.setLayout(self._statistic_layout)

        self._pg_bar = QProgressBar(self)
        self._pg_bar.setFixedWidth(200)
        self._pg_bar.setFixedHeight(20)
        self._pg_bar.setRange(0, 5)
        self._pg_bar.setFormat("%v/%m")
        self._pg_bar.setValue(0)  

        self._optionFrame_layout.addLayout(self._src_scope_layout)
        self._optionFrame_layout.addLayout(self._src_mode_layout)
        self._optionFrame_layout.addLayout(self._dsp_mode_layout)
        self._optionFrame.setLayout(self._optionFrame_layout)

        self._left_frame_layout.addWidget(self._corpusFrame)
        self._left_frame_layout.addLayout(self._input_layout)
        self._left_frame_layout.addWidget(self._optionFrame)
        self._left_frame_layout.addWidget(self._statistic_win)
        self._left_frame_layout.addWidget(self._pg_bar)

        w_n = 50
        n_n = 40
        self._stat_data = QGroupBox()
        self._stat_data.setFixedWidth(460)
        self._stat_data_layout = QGridLayout()
        self._bi_para = QLabel('双语段对：')
        self._bi_para.setToolTip('原文与译文段对齐后的段落总数')
        self._bi_para_box = QLineEdit('0')
        self._bi_para_box.setFixedWidth(w_n)
        self._bi_sent = QLabel('双语句对：')
        self._bi_sent.setToolTip('原文与译文句对齐后的段落总数')
        self._bi_sent_box = QLineEdit('0')
        self._bi_sent_box.setFixedWidth(w_n)
        self._bi_sent_ratio = QLabel('双语句比：')
        self._bi_sent_ratio.setToolTip('原文与译文原始句子比率')
        self._bi_sent_ratio_box = QLineEdit('0.00')
        self._bi_sent_ratio_box.setFixedWidth(w_n)
        self._bi_seg_ratio = QLabel('双语读比：')
        self._bi_seg_ratio.setToolTip('原文与译文原始句子片段比率')
        self._bi_seg_ratio_box = QLineEdit('0.00')
        self._bi_seg_ratio_box.setFixedWidth(w_n)
        self._ss_para = QLabel('原文段数：')
        self._ss_para.setToolTip('原文原始段落总数')
        self._ss_para_box = QLineEdit('0')
        self._ss_para_box.setFixedWidth(n_n)
        self._tt_para = QLabel('译文段数：')
        self._tt_para.setToolTip('译文原始段落总数')
        self._tt_para_box = QLineEdit('0')
        self._tt_para_box.setFixedWidth(n_n)
        self._ss_sent = QLabel('原文句数：')
        self._ss_sent.setToolTip('原文原始句子总数')
        self._ss_sent_box = QLineEdit('0')
        self._ss_sent_box.setFixedWidth(n_n)
        self._tt_sent = QLabel('译文句数：')
        self._tt_sent.setToolTip('译文原始句子总数')
        self._tt_sent_box = QLineEdit('0')
        self._tt_sent_box.setFixedWidth(n_n)
        self._ss_token = QLabel('原文形符：')
        self._ss_token.setToolTip('原文去除标点、符号、空格及纯阿伯伯数字后的字词形符总数')
        self._ss_token_box = QLineEdit('0')
        self._ss_token_box.setFixedWidth(w_n)
        self._ss_type = QLabel('原文类符：')
        self._ss_type.setToolTip('原文形符进行词性归并后的字词类符总数')
        self._ss_type_box = QLineEdit('0')
        self._ss_type_box.setFixedWidth(w_n)
        self._ss_ttr = QLabel('原文TTR：')
        self._ss_ttr.setToolTip('原文字词形符与类符比')
        self._ss_ttr_box = QLineEdit('0')
        self._ss_ttr_box.setFixedWidth(w_n)
        self._ss_sttr = QLabel('原文STTR：')
        self._ss_sttr.setToolTip('原文字词形符与类符标准比（每千词）')
        self._ss_sttr_box = QLineEdit('0')
        self._ss_sttr_box.setFixedWidth(w_n)
        self._tt_token = QLabel('译文形符：')
        self._tt_token.setToolTip('译文去除标点、符号及纯阿伯伯数字后的单词形符总数')
        self._tt_token_box = QLineEdit('0')
        self._tt_token_box.setFixedWidth(w_n)
        self._tt_type = QLabel('译文类符：')
        self._tt_type.setToolTip('译文形符进行词形还原后的单词类符总数')
        self._tt_type_box = QLineEdit('0')
        self._tt_type_box.setFixedWidth(w_n)
        self._tt_ttr = QLabel('译文TTR：')
        self._tt_ttr.setToolTip('译文单词形符与类符比')
        self._tt_ttr_box = QLineEdit('0')
        self._tt_ttr_box.setFixedWidth(w_n)
        self._tt_sttr = QLabel('译文STTR：')
        self._tt_sttr.setToolTip('译文单词形符与类符标准比（每千词）')
        self._tt_sttr_box = QLineEdit('0')
        self._tt_sttr_box.setFixedWidth(w_n)
        self._stat_data_layout.addWidget(self._bi_para,0,0)
        self._stat_data_layout.addWidget(self._bi_para_box,0,1)
        self._stat_data_layout.addWidget(self._bi_sent,1,0)
        self._stat_data_layout.addWidget(self._bi_sent_box,1,1)
        self._stat_data_layout.addWidget(self._bi_sent_ratio,2,0)
        self._stat_data_layout.addWidget(self._bi_sent_ratio_box,2,1)
        self._stat_data_layout.addWidget(self._bi_seg_ratio,3,0)
        self._stat_data_layout.addWidget(self._bi_seg_ratio_box,3,1)       
        self._stat_data_layout.addWidget(self._ss_para,0,2)
        self._stat_data_layout.addWidget(self._ss_para_box,0,3) 
        self._stat_data_layout.addWidget(self._tt_para,1,2)
        self._stat_data_layout.addWidget(self._tt_para_box,1,3)
        self._stat_data_layout.addWidget(self._ss_sent,2,2)
        self._stat_data_layout.addWidget(self._ss_sent_box,2,3)
        self._stat_data_layout.addWidget(self._tt_sent,3,2)
        self._stat_data_layout.addWidget(self._tt_sent_box,3,3)
        self._stat_data_layout.addWidget(self._ss_token,0,4)
        self._stat_data_layout.addWidget(self._ss_token_box,0,5)
        self._stat_data_layout.addWidget(self._ss_type,1,4)
        self._stat_data_layout.addWidget(self._ss_type_box,1,5)
        self._stat_data_layout.addWidget(self._ss_ttr,2,4)
        self._stat_data_layout.addWidget(self._ss_ttr_box,2,5) 
        self._stat_data_layout.addWidget(self._ss_sttr,3,4)
        self._stat_data_layout.addWidget(self._ss_sttr_box,3,5)
        self._stat_data_layout.addWidget(self._tt_token,0,6)
        self._stat_data_layout.addWidget(self._tt_token_box,0,7)
        self._stat_data_layout.addWidget(self._tt_type,1,6)
        self._stat_data_layout.addWidget(self._tt_type_box,1,7)
        self._stat_data_layout.addWidget(self._tt_ttr,2,6)
        self._stat_data_layout.addWidget(self._tt_ttr_box,2,7)   
        self._stat_data_layout.addWidget(self._tt_sttr,3,6)
        self._stat_data_layout.addWidget(self._tt_sttr_box,3,7)
        self._stat_data.setLayout(self._stat_data_layout)

        self._task_window = QGroupBox()
        self._task_window_layout = QGridLayout()
        self._read_opt_btn = QLabel('阅读模式：')
        self._read_opt_btn.setToolTip('按指定模式展示语料内容')
        self._read_opt = QComboBox()
        self._read_opt.setToolTip('选择当前语料内容展示模式')
        self._read_opt.addItem("原语全文")
        self._read_opt.addItem("译语全文")
        self._read_opt.addItem("双语段对齐")
        self._read_opt.addItem("双语句对齐")
        self._freq_opt_btn = QPushButton('统计词频')
        self._freq_opt_btn.setToolTip('统计指定语料的词频')
        self._freq_opt_btn.clicked.connect(self.freqcount_output)
        self._cloud_opt_btn = QPushButton('绘制词云')
        self._cloud_opt_btn.setToolTip('依据拽定语料词频绘制词云图片')
        self._cloud_opt_btn.clicked.connect(self.wordcloud_output)
        self._elem_opt_btn = QPushButton('提取元素')
        self._elem_opt_btn.setToolTip('从当前语料中提取思政元素')
        self._elem_opt_btn.clicked.connect(self.quote_display)
        self._trans_opt_btn = QPushButton('抽取习题')
        self._trans_opt_btn.setToolTip('从当前语料中随机抽取翻译习题')
        self._trans_opt_btn.clicked.connect(self.quiz_display)
        self._task_window_layout.addWidget(self._read_opt_btn, 0,0)
        self._task_window_layout.addWidget(self._read_opt, 0,1)
        self._task_window_layout.addWidget(self._freq_opt_btn, 1,0)
        self._task_window_layout.addWidget(self._cloud_opt_btn, 1,1)
        self._task_window_layout.addWidget(self._elem_opt_btn, 2,0)
        self._task_window_layout.addWidget(self._trans_opt_btn, 2,1)
        self._task_window.setLayout(self._task_window_layout)  
        
        self._corpus_data_form = QGroupBox('当前语料概况')
        self._corpus_data_form.setAlignment(Qt.AlignCenter)
        self._corpus_data_form.setFixedHeight(150)
        self._corpus_data_form_layout = QHBoxLayout()
        self._corpus_data_form_layout.addWidget(self._stat_data)
        self._corpus_data_form_layout.addWidget(self._task_window)
        self._corpus_data_form.setLayout(self._corpus_data_form_layout)
        
        self._src_result_form = QGroupBox('双语检索结果')
        self._src_result_form.setAlignment(Qt.AlignCenter)
        self._result_window = QTextBrowser(parent)
        self._result_window.setFrameStyle(0)
        self._result_window.setWordWrapMode(QTextOption.WordWrap)
        self._result_window.setStyleSheet("QTextBrowser{border-image: url(./app_data/images/frontPageDefault.png);}")
        self._src_result_formLayout = QHBoxLayout()
        self._src_result_formLayout.addWidget(self._result_window)
        self._src_result_form.setLayout(self._src_result_formLayout)

        self._next_page_button=QPushButton()
        self._next_page_button.setText('>>>>> 点击加载更多检索结果 <<<<<')
        self._next_page_button.clicked[bool].connect(self.print_result)
        self._next_page_button.setDisabled(True)
        self._next_page_button.setToolTip('分页展示每100组检索结果')
        
        self._right_frame_layout = QVBoxLayout()
        self._right_frame_layout.addWidget(self._corpus_data_form)
        self._right_frame_layout.addWidget(self._src_result_form)
        self._right_frame_layout.addWidget(self._next_page_button)

        mainWidget = QWidget()
        mainLayout = QHBoxLayout(mainWidget)
        mainLayout.setSpacing(2)
        mainLayout.addLayout(self._left_frame_layout)
        mainLayout.addLayout(self._right_frame_layout)
        self.setCentralWidget(mainWidget)

        self._statusBar = QStatusBar()
        self._statusBar.showMessage('欢迎使用 外语教学语料辅助平台V1.0')
        self._copyRightLabel = QLabel("抚顺职业技术学院 张修海 © 2024 版权所有（软著登字第13473683号）")
        self._statusBar.addPermanentWidget(self._copyRightLabel)
        self.setStatusBar(self._statusBar)

        self.setGeometry(200, 50, 960, 650)
        self.setObjectName("MainWindow")
        self.setWindowTitle("外语教学语料辅助平台V1.0")
        
        self.setWindowIcon(QIcon(currentDir + "/app_data/workfiles/myIcon.png"))
        self.setIconSize(QSize(100, 40))

        self._corpora = None
        self._current_corpus = None

        self._corpusFrame.setMaximumWidth(250)
        self._optionFrame.setMaximumWidth(250)
        
    def find_parents(self,item):
        pa = item.parent()
        if pa is None:
            return item.text(0),""
        else:
            return pa.text(0),item.text(0)
        
    def set_corpora_list(self, corpus_ids: [], corpora: []):
        self._corpusWindow = QTreeWidget()
        self._corpusWindow.setStyleSheet("QTreeWidget{background-color:%s;border-image: url(./app_data/images/bg.png);border:0px;}"% ("WhiteSmoke"))
        self._corpusWindow.setFixedWidth(220)
        self._corpusWindow.setMaximumWidth(220)
        self._corpusWindow.setFixedHeight(250)
        self._corpusWindow.setSortingEnabled(False)        
        self._corpusWindow.setColumnCount(1)
        self._corpusWindow.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._corpusWindow.itemSelectionChanged.connect(self.selecting_item)
        self._corpusWindow.itemDoubleClicked.connect(self.openCurrentFileRequest)
        self._corpusWindow.customContextMenuRequested.connect(self.listItemRightClicked)        
        self._corpusWindow.setHeaderHidden(True)
        cat_list = []
        for corp_id in corpus_ids:
            stem = corp_id.split(".")[0]
            if stem not in cat_list:
                cat_list.append(stem)
        root_list = []
        for cat in cat_list:
            root = QTreeWidgetItem()
            root.setText(0, cat)
            root_list.append(root)
            for corp_id in corpus_ids:
                if corp_id.startswith(cat) and  "UXEP" not in corp_id:
                    child = QTreeWidgetItem()
                    child.setText(0,corp_id)
                    root.addChild(child)                    
                    root_list.append(child)
                elif corp_id.startswith(cat) and  "UXEP" in corp_id:
                    for corp in corpora:
                        if corp_id == corp[1]:
                            current_corpus = self.open_dat_file(corp[0])
                            for article in current_corpus.articles:
                                child = QTreeWidgetItem()
                                child.setText(0, str(article.num) + " - " + article.title_zh)                                                         
                                root.addChild(child)
                                root_list.append(child) 
                            break
                else:
                    pass
        if root_list:
            self._corpusWindow.insertTopLevelItems(0,root_list)
            self._corpusFrameLayout.addWidget(self._corpusWindow, alignment=Qt.AlignTop)
            self._corpusFrame.setLayout(self._corpusFrameLayout)
        self._corpusFrame.setTitle(f"语料列表（{len(corpus_ids)}）")
        self._corpora = corpora
        
    def reload_corpora_list(self, corpus_ids: [], corpora: []):
        old_root = self._corpusWindow.invisibleRootItem()
        child_count = old_root.childCount()
        for i in range(child_count):
            child = old_root.child(i)
            old_root.removeChild(child)
        self._corpusWindow.clear()
        cat_list = []       
        for corp_id in corpus_ids:
            stem = corp_id.split(".")[0]
            if stem not in cat_list:
                cat_list.append(stem)
        root_list = []
        for cat in cat_list:
            root = QTreeWidgetItem()
            root.setText(0, cat)
            root_list.append(root)
            for corp_id in corpus_ids:
                if corp_id.startswith(cat):
                    child = QTreeWidgetItem()
                    child.setText(0,corp_id)
                    root.addChild(child)
                    root_list.append(child)
        if root_list:
            self._corpusWindow.insertTopLevelItems(0,root_list) 
        self._corpusFrame.setTitle(f"语料列表（{len(corpus_ids)}）")
            
    def reader_check_opt(self):
        return self._read_opt.currentIndex()    
        
    def reader_check_corpus(self):
        warning_info = ""
        if self._current_corpus:
            pass
        else:
            warning_info = "请先指定当前语料，再开始阅读！"
        return warning_info

    def reader_get_current_text(self, current_corpus):
        lang_opt = self.reader_check_opt()
        if lang_opt == 0:
            text_to_display = current_corpus.raw_text_zh
        elif lang_opt == 1:
            text_to_display = current_corpus.raw_text_en
        else:
            text_to_display = self.reader_get_bitext(current_corpus,lang_opt)
        return text_to_display
    
    def reader_get_bitext(self, current_corpus, opt):
        text = ""
        passages = []
        if opt == 2:
            for para in current_corpus.paras:
                sents_zh = []
                sents_en = []
                for sent in para.sents:
                    sents_zh.append(sent.zh)
                    sents_en.append(sent.en)
                para_zh = "".join(sents_zh)
                para_en = " ".join(sents_en)
                passages.append(para_zh + "\n" + para_en)          
            if passages:
                text = "\n".join(passages)
        elif opt == 3:
            for para in current_corpus.paras:
                for sent in para.sents:
                    passages.append(sent.zh + "\n" + sent.en)
            if passages:
                text = "\n".join(passages)
        else:
            pass
        return text            
        
    def text_reader(self):
        warning = self.reader_check_corpus()
        if warning:
            self.set_status_text(warning)
        else:
            if self._current_corpus.genre_en not in ["governance of china", "educational philosophy"]:
                date = self._current_corpus.date_zh.replace("[DT]","")
                if "（" not in date:
                    date = "（"+ date + "）"
                show_title = "《"+ self._current_corpus.title_zh + "》" + date
            elif self._current_corpus.genre_en == "governance of china":
                show_title = "《"+ self._current_corpus.title_zh + "》" \
                             + self._current_corpus.volume_id_zh \
                             + self._current_corpus.edition_id_zh
            else:
                show_title = "《"+ self._current_corpus.title_zh + "》" \
                             + self._current_corpus.edition_id_zh
            self._corpus_data_form.setTitle("当前语料:"+show_title)
            text_to_show = self.reader_get_current_text(self._current_corpus)
            self._result_window.clear()
            self._result_window.setPlainText(text_to_show)
            self._result_window.setStyleSheet("QTextBrowser{background-color:%s;border-image: url(./app_data/images/rd_bg.png);border:0px;}"% ("WhiteSmoke"))
            self._src_result_form.setTitle("当前语料内容")
            self.reset_result_image()

    def get_current_text(self, current_corpus):
        lang_opt = self.reader_check_opt()
        if lang_opt == 0:
            text_to_display = current_corpus.raw_text_zh
        elif lang_opt == 1:
            text_to_display = current_corpus.raw_text_en
        else:
            text_to_display = self.reader_get_bitext(current_corpus,lang_opt)
        return text_to_display
            
    def fill_out_stats(self, corpus):
        self._bi_para_box.setText(f"{corpus.bi_para_count}")
        self._bi_sent_box.setText(f"{corpus.bi_sent_count}")
        self._bi_sent_ratio_box.setText(f"{corpus.bi_sent_ratio}")
        self._bi_seg_ratio_box.setText(f"{corpus.bi_seg_ratio}")
        self._ss_para_box.setText(f"{corpus.zh_para_count}")
        self._tt_para_box.setText(f"{corpus.en_para_count}")
        self._ss_sent_box.setText(f"{corpus.zh_sent_count}")
        self._tt_sent_box.setText(f"{corpus.en_sent_count}")
        self._ss_token_box.setText(f"{corpus.zh_word_token_count}")
        self._ss_type_box.setText(f"{corpus.zh_word_type_count}")
        self._tt_token_box.setText(f"{corpus.en_word_token_count}")
        self._tt_type_box.setText(f"{corpus.en_word_type_count}")
        if corpus.zh_word_ttr == 0:
            self._ss_ttr_box.setText("0")
        else:
            self._ss_ttr_box.setText(f"{corpus.zh_word_ttr*100:.2f}%")
        if corpus.zh_word_sttr == 0:
            self._ss_sttr_box.setText("0")
        else:
            self._ss_sttr_box.setText(f"{corpus.zh_word_sttr*100:.2f}%")
        if corpus.en_word_ttr == 0:
            self._tt_ttr_box.setText("0")
        else:
            self._tt_ttr_box.setText(f"{corpus.en_word_ttr*100:.2f}%")
        if corpus.en_word_sttr == 0:
            self._tt_sttr_box.setText("0")
        else:
            self._tt_sttr_box.setText(f"{corpus.en_word_sttr*100:.2f}%")            
        self._src_scope_3.setChecked(True)
  
    def openCurrentFileRequest(self, item):
        i = item.text(0)
        for corp in self._corpora:
            if corp[1].split(".")[0] not in ["UXEP"]:
                if i == corp[1]:
                    corpus = self.open_dat_file(corp[0])                
                    self._current_corpus = (corpus,"")
                    self.update_current_corpus.emit(corpus.title_zh)
                    break
            else:
                temp_corpus = self.open_dat_file(corp[0])
                for art in temp_corpus.articles:
                    if  i.split(" - ")[1] == art.title_zh:
                        self._current_corpus = (self.open_dat_file(corp[0]),art)                        
                        self.update_current_corpus.emit(art.title_zh)
                        break                        
        if self._current_corpus:
            self.load_tag_corpus.emit('start')
            main_corpus = self._current_corpus[0]
            art_corpus = self._current_corpus[1]
            if art_corpus:
                show_title = "《"+main_corpus.title_zh+"·"+art_corpus.title_zh + "》"
                self.fill_out_stats(art_corpus)
                text_to_show = self.get_current_text(art_corpus)                            
            else:
                date = main_corpus.date_zh.replace("[DT]","")
                if "（" not in date:
                    date = "（"+ date + "）"
                show_title = "《"+ main_corpus.title_zh + "》" + date
                self.fill_out_stats(main_corpus)
                text_to_show = self.get_current_text(main_corpus)                
            self._result_window.clear()
            self._result_window.setPlainText(text_to_show)
            self.reset_result_image()
            self._corpus_data_form.setTitle("当前语料:"+show_title)
            self._src_result_form.setTitle("当前语料内容")
            self.update_current_corpus.emit(show_title)
        else:
            self._corpus_data_form.setTitle("当前语料概况")
            self._src_result_form.setTitle("双语检索结果")
            
    def word_cloud_producer(self):
        pass        
       
    def check_src_scopes(self):
        if self._src_scope_1.isChecked():
            return 1
        if self._src_scope_2.isChecked():
            return 2
        if self._src_scope_3.isChecked():
            return 3
        if self._src_scope_4.isChecked():
            return 4 

    def search_scope(self) -> SearchScope:           
        if self._src_scope_2.isChecked():
            return SearchScope.SELECTED
        if self._src_scope_3.isChecked():
            return SearchScope.CURRENT
        if self._src_scope_4.isChecked():
            return SearchScope.GENRE
        return SearchScope.ALL
    
    def listItemRightClicked(self):
        pass

    def open_dat_file(self, dat_file):
        dat_read = ''
        with open(dat_file, 'rb') as f:
            dat_read = pickle.load(f)
        return dat_read
        
    def reset_result_image(self):
        self._result_window.setStyleSheet("QTextBrowser{background-color:%s;border-image: url(./app_data/images/rd_bg.png);border:0px;}"% ("WhiteSmoke"))

    def set_status_text(self, text):
        self._statusBar.showMessage(text, 10000)        
    
    def set_corpus(self, corpus):
        self._corpus = corpus

    def search_mode(self) -> SearchMode:
        if self._src_mode_1.isChecked():
            return SearchMode.NORMAL
        if self._src_mode_3.isChecked():
            return SearchMode.REGEX
        return SearchMode.EXTENDED

    def search_text(self):
        return self._input_box.text()    
          
    def set_result_html(self, html):
        self._src_result_form.setTitle("双语检索结果")
        self._result_window.setStyleSheet("QTextBrowser{background-color:%s;border-image: url(./app_data/images/rd_bg.png);border:0px;}"% ("WhiteSmoke"))
        self._result_window.setHtml(html)    
        
    def display_mode(self):
        return [self.display_context(), self.display_source]
    
    def display_context(self):
        return 1 if self._dsp_context_button.isChecked() else 0

    def display_source(self):
        return 1 if self._dsp_source_button.isChecked() else 0

    def display_note(self):
        return 1 if self._dsp_note_button.isChecked() else 0
    
    def display_check(self):
        return [self.display_note(), self.display_source(), self.display_context()]

    def _info(self):
        QMessageBox.about(self, "软件信息",
                          '''<p align='center'>外语教学语料辅助平台<br>
                             Bilingual Corpus-Aided Platform <br>
                             For Foreign Languages Pedagogical Education<br>                            
                             Windows 标准版 V1.0<br>
                          （软著登字第13473683号）<br>
                          版权归属：张修海 抚顺职业技术学院外语系<br>
                          联系方式：42716403@qq.com</p>''')        

    def _quest(self, i, k):
        r = 'N'
        if k == "None":
            reply = QMessageBox.warning(self, "温馨提示",
                                        f'''<p align='center'>抱歉，未找到任何有效的语料文件！<br>
                                            请将要检索的一个或多个dat文件放入<br>
                                            app_data/temp_data/<br>
                                            或将原始的一个或多个json文件放入<br>
                                            app_data/corpus/<br>
                                            然后再重新运行本软件。''', QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                r = 'O'
        else:
            reply = QMessageBox.warning(self, "温馨提示",
                                        f'''<p align='center'>尚有{i}个语料文件缺少DATA文档！<br>
                                            为提高检索速度，建议现在生成，<br>
                                            是否需要现在自动生成DATA文件？''', QMessageBox.Ok | QMessageBox.Ignore)
            if reply == QMessageBox.Ok:
                r = 'Y'
        return r
    
    def resizeFontUp(self):        
        font_size = self.font.pointSize()+1
        font_family = self.font.family()
        self.font = QFont(font_family, font_size)
        self._result_window.setFont(self.font)
    
    def resizeFontDown(self):
        font_size = self.font.pointSize()-1
        font_family = self.font.family()
        self.font = QFont(font_family, font_size)
        self._result_window.setFont(self.font)
        
    def keyReleaseEvent(self, event):
        if event.key()==Qt.Key_Enter or event.key()==Qt.Key_Return:
            self.search()
        modifiers = event.modifiers()
        if modifiers == (Qt.ControlModifier) and event.key()==Qt.Key_S:
            self._input_box.clear()
            self._input_box.setFocus()
