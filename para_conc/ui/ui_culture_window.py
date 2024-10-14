#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

from PySide6.QtWidgets import QMainWindow, QTextEdit, QLabel, QGridLayout, QVBoxLayout,\
     QHBoxLayout, QPushButton, QGroupBox, QCheckBox, QLineEdit,QStatusBar, QComboBox, QCompleter
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
import os, sys, re, random, json
from PySide6.QtWidgets import QApplication
from collections import defaultdict

from para_conc.ui.ui_main_window import UIMainWindow
from para_conc.core.thread_elm_obtainer import ElmObtainerThread
from para_conc.core.lg_dict import LG_DICT

class CulWindow(QMainWindow):
    update_pbar = Signal([int, int])
    get_corpus = Signal(str)
    def __init__(self, parent=None):
        super(CulWindow, self).__init__(parent)
        self.setWindowTitle('内容提取')
        self.setFixedSize(500, 400)
        currentDir = os.getcwd()
        self.setWindowIcon(QIcon(currentDir + "/app_data/images/vquote.png"))
        self.setIconSize(QSize(100, 40))
        self._statusBar = QStatusBar()
        self.setStatusBar(self._statusBar)        
        workDir = os.path.join(currentDir, "app_data","workfiles")
        self.saveDir = os.path.join(currentDir,"saved_files")
        self.dict_file = os.path.join(workDir, "quotation_data.json")
        self._header_img = os.path.join(currentDir, "app_data","images", 'quote_title.png')
        self.lgd = LG_DICT['2']
        self._current_corpus = ""
        self._text_corpus = ""
        self._current_file_id = ""
        self._current_elem_html = ""
        self._current_elem_text =""
        max_width = 460
        max_height = 400
        self.current_dict = {}
        self.current_quote = ""
        self.current_id = ""
        self.quotes = {}
        self.quote_keys ={}
        self.prompt_list = []
       
        self._main_frame= QLabel()
        self._main_frame_layout = QVBoxLayout()

        self._header_label = QLabel()
        self._header_label.setFixedWidth(400)
        self._header_label.setFixedHeight(80)
        self._header_label.setStyleSheet("QLabel{border-image: url(./app_data/images/quote_title.png);}")
        
        self._corp_title = QLabel("当前语料中文标题:")
        self._corp_title_box = QLineEdit()
        self._corp_title_box.setReadOnly(True)
        
        self._corp_info_layout = QGridLayout()
        self._corp_info_layout.addWidget(self._corp_title, 0, 0)
        self._corp_info_layout.addWidget(self._corp_title_box, 0, 1)

        self._show_frame= QGroupBox("提取结果", alignment=Qt.AlignCenter)
        self._show_frame_layout = QVBoxLayout()
        self._quote_window = QTextEdit()
        self._quote_window.setFixedWidth(max_width)
        self._quote_window.setReadOnly(True)

        self._show_frame_layout.addWidget(self._quote_window, alignment=Qt.AlignCenter|Qt.AlignTop)
        self._show_frame.setLayout(self._show_frame_layout)
        
        btn_max = 100
        btn_min = 80

        self._btn_layout = QHBoxLayout()
       
        self._get_quote_btn = QPushButton("提取引言元素")
        self._get_quote_btn.clicked[bool].connect(self.get_quote_data)
        self._get_quote_btn.setFixedWidth(btn_max)
        self._get_elem_btn = QPushButton("提取其他元素")
        self._get_elem_btn.clicked[bool].connect(self.get_elem_data)
        self._get_elem_btn.setFixedWidth(btn_max)
        self._quit_btn = QPushButton("关闭退出")        
        self._quit_btn.clicked[bool].connect(self.close)
        self._quit_btn.setFixedWidth(btn_min)
        self._save_btn = QPushButton("输出结果")
        self._save_btn.clicked[bool].connect(self.save_data)
        self._save_btn.setFixedWidth(btn_min)
        self._btn_layout.addWidget(self._get_quote_btn)
        self._btn_layout.addWidget(self._get_elem_btn)
        self._btn_layout.addWidget(self._save_btn)
        self._btn_layout.addWidget(self._quit_btn)

        self._main_frame_layout.addWidget(self._header_label, alignment=Qt.AlignTop|Qt.AlignCenter)
        self._main_frame_layout.addStretch(1)
        self._main_frame_layout.addLayout(self._corp_info_layout)
        self._main_frame_layout.addStretch(1)
        self._main_frame_layout.addWidget(self._show_frame, alignment=Qt.AlignTop)
        self._main_frame_layout.addStretch(6)
        self._main_frame_layout.addLayout(self._btn_layout)
        self._main_frame_layout.addStretch(0)
        
        self._main_frame.setLayout(self._main_frame_layout)
        self.setCentralWidget(self._main_frame)

        self.load_data()
        
    def thread_run(self, request, key):
        self.getter = ElmObtainerThread(request, key)
        self.getter.finished.connect(self.getter.deleteLater)
        self.getter.pbar_signal.connect(self.update_pbar)
        self.getter.msg_m_signal.connect(self.set_status_text)
        self.getter.output_signal.connect(self.update_content)
        self.getter.start()
        
    def update_content(self,m,n):
        self.result = m
        self.error = n
        if self.result:
            self._current_elem_text = self.result.replace("\n\n",'\n')
            self._quote_window.clear()
            self._quote_window.setText(self._current_elem_text)
        else:
            if self.error:
                self.set_status_text(f"抱歉，其他思政元素提取失败，错误代码：{self.error}")
            else:
                self.set_status_text("抱歉，其他思政元素提取失败，请检查网络是否畅通")
    
    def load_data(self):                      
        if self.current_dict:
            self.quotes = {}
            self.quote_keys = {}
            for k, y in sorted(self.current_dict.items(), key=lambda k:int(k[0])):
                kwds = []
                item = y['quote'].strip()
                kwds.append(item)
                alias = y.get('alias',"")
                if alias:
                    kwds.extend([x for x in alias.split('|') if x])
                quote_kwds = "|".join(kwds)
                self.quote_keys[k] = quote_kwds
                self.quotes[k]= item                
            for (k, v) in self.current_dict.items():
                if v['quote'] == self.current_quote:
                    self.current_id = k
                    break
        else:
            with open(self.dict_file, mode="rt", encoding = "utf-8-sig") as f:
                self.prompt_list.clear()          
                self.current_dict = json.load(f)  
                self.quotes = {}                 
                for key, y in self.current_dict.items():                    
                    kwds = []
                    item = y['quote'].strip()
                    kwds.append(item)
                    alias = y.get('alias',"")
                    if alias:
                        kwds.extend([x for x in alias.split('|') if x])
                    sorted_list = sorted(kwds, key=lambda x:len(x), reverse=True)    
                    quote_kwds = "|".join(sorted_list)
                    self.quote_keys[key] = quote_kwds 
                    self.quotes[key]= item
            for (k, v) in self.current_dict.items():
                if v['quote'] == self.current_quote:
                    self.current_id = k
                    break             
        
    def get_quote_data(self):
        self._quote_window.clear()
        self._current_elem_html = ""
        self._current_elem_text = ""
        self.get_corpus.emit('get_corpus')
        if self._current_corpus:
            if self._current_corpus[1]:
                current_corpus = self._current_corpus[1]
            else:
                current_corpus = self._current_corpus[0]
        if current_corpus:
            show_title = current_corpus.title_zh
            self._corp_title_box.setText(show_title)
            my_dict = defaultdict(list)
            tempt_result = []
            for key, quote in self.quote_keys.items():
                m = re.findall(quote, current_corpus.raw_text_zh)
                if m:
                    for n in m:
                        if key not in my_dict.keys():
                            my_dict[key]=[]
                            my_dict[key].append(n)
                        else:
                            if n not in my_dict[key]:
                                my_dict[key].append(n)
            quote_num = len(my_dict.keys())
            if my_dict:
                result_dict = {}
                para_tank = current_corpus.paras
                for para in para_tank:
                    for i, keys in my_dict.items():
                        reg = "|".join(keys)
                        src = re.findall(reg, para.raw_text_zh)
                        rpl_wrds = []
                        if src:
                            for rst in src:
                                if rst not in rpl_wrds:
                                    rpl_wrds.append(rst)
                        if rpl_wrds:
                            pair_found = (para.raw_text_zh, para.raw_text_en)
                            if pair_found not in result_dict.keys():
                                result_dict[pair_found]=defaultdict(list)
                                result_dict[pair_found]['index'].append(i)
                                result_dict[pair_found]['terms'].extend(rpl_wrds)
                            else:
                                if i not in result_dict[pair_found]['index']:
                                    result_dict[pair_found]['index'].append(i)
                                if rpl_wrds not in result_dict[pair_found]['terms']:
                                    result_dict[pair_found]['terms'].extend(rpl_wrds)                                   

                if result_dict:
                    result_list = []
                    final_quote_num = 0                    
                    for bi_sent, index_terms in result_dict.items():
                        sent_zh = bi_sent[0]
                        sent_en = bi_sent[1]
                        rpl_terms = list(set(index_terms['terms']))
                        keys = list(set(index_terms['index']))
                        for term in rpl_terms:
                            sent_zh = re.sub(term, '<font color = "red">'+term+'</font>', sent_zh)
                        case_contents = "【原文】<br>"+sent_zh+"<br>【译文】<br>"+sent_en
                        case_contents = re.sub(r'\[PS\]', "", case_contents)
                        if len(keys)==1:
                            case_head = '<b>☆<font color = "blue">'+self.current_dict[keys[0]]['quote']+'</font>☆</b>'
                            case_origin = "【原典】<br>" + self.current_dict[keys[0]]['origin'] + "<br>——" + self.current_dict[keys[0]]['source']
                            case_meaning = "【释意】<br>" + self.current_dict[keys[0]]['meaning']
                            case_origin = case_origin.replace("|","<br>")
                            case_meaning = case_meaning.replace("|","<br>")
                            info_string = case_origin+"<br>"+case_meaning
                            final_quote_num += 1
                        else:
                            info = []
                            info_string = ""
                            case_heads = []
                            for num, key in enumerate(keys, start=1):
                                head = '<b>☆<font color = "blue">'+self.current_dict[key]['quote']+'</font>☆</b>'
                                if head not in case_heads:
                                    case_heads.append(head)
                                    final_quote_num += 1
                                    case_origin = "【原典】<br>" + self.current_dict[key]['origin'] + "<br>——" + self.current_dict[key]['source']
                                    case_meaning = f"【释意】<br>" + self.current_dict[key]['meaning']
                                    case_origin = case_origin.replace("|","<br>")
                                    case_meaning = case_meaning.replace("|","<br>")
                                    info.append(case_origin+"<br>"+case_meaning)
                            if info:
                                info_string = "<br>".join(info)
                            case_head = "<br>".join(case_heads)
                        final_result = case_head+"<br>"+case_contents + "<br>" + info_string
                        if final_result not in result_list:
                            result_list.append(final_result)
                    if result_list:
                        result_count = f"本次从此篇语料中共提取出{final_quote_num}条引言典故元素:"
                        result_html = result_count + "<br>"+"<br>".join(result_list)
                        self._current_elem_html = result_html
                        self._current_file_id = self._corp_title_box.text().replace(" ","").replace("\n","")
                        self._quote_window.setHtml(result_html)
                    self.set_status_text("引言典故元素提取取成功！")
            else:                
                self.set_status_text("当前语料中未检索到引言典故项。")
        else:
            self.set_status_text("待检索文件缺失，请先加载当前语料。")

    def get_elem_data(self):
        self._quote_window.clear()
        self._current_elem_html = ""
        self._current_elem_text = ""
        self.get_corpus.emit('get_corpus')
        if self._current_corpus:
            if self._current_corpus[1]:
                current_corpus = self._current_corpus[1]
            else:
                current_corpus = self._current_corpus[0]
        else:
            current_corpus = ""
        if current_corpus:            
            question_stem = "你是一个思政元素提取专家，你的任务是从以下文本中为用户提供专业、准确的思政元素，回复时请用中文：\n"            
            element_request = question_stem + current_corpus.raw_text_zh
            self.thread_run(element_request, self.lgd)            
        else:
            self.set_status_text("待检索文件缺失，请先加载当前语料。")
            
    def save_data(self):
        current_id = self._corp_title_box.text().replace(" ","").replace("\n","")
        if self._current_file_id and self._current_elem_html:
            if current_id == self._current_file_id:
                fileToSave = os.path.join(self.saveDir, self._current_file_id+"_引言典故.txt")
                result_txt = re.sub("<br>","\n", self._current_elem_html)
                result_txt = re.sub(r"<.*?>","", result_txt)
                title = "《"+self._current_file_id+"》中的引言典故"
                with open(fileToSave, "wt", encoding = "utf-8-sig") as f:
                    f.write(title+"\n"+result_txt)
                    self.set_status_text("当前引言典故提取结果已成功保存到本地！")
            else:
                self.set_status_text("当前提取结果为空：请先抽取引言，再保存结果！")
        elif self._current_file_id and self._current_elem_text:
            if current_id == self._current_file_id:
                fileToSave = os.path.join(self.saveDir, self._current_file_id+"_其他元素.txt")
                title = "《"+self._current_file_id+"》中的思政元素"
                with open(fileToSave, "wt", encoding = "utf-8-sig") as f:
                    f.write(title+"\n"+self._current_elem_text)
                    self.set_status_text("当前其他元素提取结果已成功保存到本地！")
            else:
                self.set_status_text("当前提取结果为空：请先抽取其他元素，再保存结果！")
        elif self._current_file_id:
            self.set_status_text("抱歉，请先抽取所需元素！")
        elif self._current_elem_html:
            self.set_status_text("抱歉，请先加载当前语料！")
        else:
            self.set_status_text("抱歉，请先加载当前语料！")
    
    def write_to_json(self, data):
        with open(self.dict_file, 'wt', encoding='utf-8-sig')as f:
            json.dump(data, f)
            self.set_status_text("文件已保存！")
            
    def set_status_text(self, text):
        self._statusBar.showMessage(text, 3000) 

class CulDictWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CulDictWindow, self).__init__(parent)
        self.setWindowTitle('引言语料编辑')
        self.setFixedSize(500,480)
        self._statusBar = QStatusBar()
        self.setStatusBar(self._statusBar)
        currentDir = os.getcwd()
        self.setWindowIcon(QIcon(currentDir + "/app_data/images/qdict.png"))
        self.setIconSize(QSize(100, 40))
        workDir = os.path.join(currentDir, "app_data","workfiles")
        self.saveDir = os.path.join(currentDir,"saved_files")
        self.dict_file = os.path.join(workDir, "quotation_data.json")
        
        max_width = 400
        max_height = 450
        self.current_dict = {}
        self.current_quote = ""
        self.current_id = ""
        self.quotes = []
        self.prompt_list = [] 
        
        self._main_frame= QGroupBox()
        self._main_frame_layout = QVBoxLayout()

        self._setting_frame= QGroupBox()
        self._setting_frame_layout = QGridLayout()

        self._add_label = QLabel("新增：")
        self._add_box = QLineEdit()
        self._add_box.setFixedWidth(max_width)

        self._id_label = QLabel("序号：")
        self._id_box = QLineEdit()
        self._id_box.setFixedWidth(50)
        
        self._quote_label = QLabel("引言：")
        self._quote_box = QComboBox()
        self._quote_box.setFixedWidth(max_width-100)
        self._quote_box.currentIndexChanged.connect(self.display_data)

        self._alias_label = QLabel("变体：")
        self._alias_box = QLineEdit()
        self._alias_box.setFixedWidth(max_width)
        
        self._source_label = QLabel("出处：")
        self._source_box = QLineEdit()
        self._source_box.setFixedWidth(max_width)

        self._origin_label = QLabel("原典：")
        self._origin_box = QTextEdit()
        self._origin_box.setFixedWidth(max_width)
        self._origin_box.setFixedHeight(50)
        
        self._meaning_label = QLabel("释义：")
        self._meaning_box = QTextEdit()
        self._meaning_box.setFixedWidth(max_width)

        self._date_label = QLabel("年代：")
        self._date_box = QLineEdit()
        self._date_box.setFixedWidth(max_width)
        
        self._category_label = QLabel("类别：")
        self._category_box = QLineEdit()
        self._category_box.setFixedWidth(max_width)

        self._body_layout = QHBoxLayout()

        self._setting_frame_layout.addWidget(self._id_label, 0, 0)
        self._setting_frame_layout.addWidget(self._id_box, 0, 1)
        self._setting_frame_layout.addWidget(self._quote_label, 0, 2)
        self._setting_frame_layout.addWidget(self._quote_box, 0, 3)
        self._setting_frame_layout.addWidget(self._alias_label, 1, 0)
        self._setting_frame_layout.addWidget(self._alias_box, 1, 1,1,3)
        self._setting_frame_layout.addWidget(self._source_label, 2, 0)
        self._setting_frame_layout.addWidget(self._source_box, 2, 1,1,3)
        self._setting_frame_layout.addWidget(self._origin_label, 3, 0)
        self._setting_frame_layout.addWidget(self._origin_box, 3, 1,1,3)
        self._setting_frame_layout.addWidget(self._meaning_label, 4, 0)
        self._setting_frame_layout.addWidget(self._meaning_box, 4, 1,1,3)
        self._setting_frame_layout.addWidget(self._date_label, 5, 0)
        self._setting_frame_layout.addWidget(self._date_box, 5, 1,1,3)
        self._setting_frame_layout.addWidget(self._category_label, 6, 0)
        self._setting_frame_layout.addWidget(self._category_box, 6, 1,1,3)
        self._setting_frame_layout.addWidget(self._add_label, 7, 0)
        self._setting_frame_layout.addWidget(self._add_box, 7, 1,1,3)
        
        self._setting_frame.setLayout(self._setting_frame_layout)
        
        btn_max = 80

        self._btn_layout = QHBoxLayout()
        
        self._quit_btn = QPushButton("关闭退出")        
        self._quit_btn.clicked[bool].connect(self.close)
        self._quit_btn.setFixedWidth(btn_max)
        self._modify_btn = QPushButton("修改辞条")
        self._modify_btn.clicked[bool].connect(self.update_data)
        self._modify_btn.setFixedWidth(btn_max)
        self._add_btn = QPushButton("新增辞条")
        self._add_btn.clicked[bool].connect(self.add_data)
        self._add_btn.setFixedWidth(btn_max)
        self._del_btn = QPushButton("删除辞条")
        self._del_btn.clicked[bool].connect(self.del_data)
        self._del_btn.setFixedWidth(btn_max)
        self._save_btn = QPushButton("保存语料")
        self._save_btn.clicked[bool].connect(self.save_data)
        self._save_btn.setFixedWidth(btn_max)
        self._btn_layout.addWidget(self._add_btn)
        self._btn_layout.addWidget(self._modify_btn)        
        self._btn_layout.addWidget(self._del_btn)
        self._btn_layout.addWidget(self._save_btn)
        self._btn_layout.addWidget(self._quit_btn)

        self._main_frame_layout.addWidget(self._setting_frame)
        self._main_frame_layout.addStretch(6)
        self._main_frame_layout.addLayout(self._btn_layout)
        self._main_frame_layout.addStretch(1)
        self._main_frame.setLayout(self._main_frame_layout)
        self.setCentralWidget(self._main_frame)

        self.load_data()

    def load_data(self):
        if self.current_dict:
            self._quote_box.clear()
            self.quotes = {}
            for k, y in sorted(self.current_dict.items(), key=lambda k:int(k[0])):
                kwds = []
                item = y['quote'].strip()
                self.quotes[k]= item                
                self.prompt_list.append(item)
            self._quote_box.addItems(self.quotes.values())
            self.current_quote = self._quote_box.currentText()
            for (k, v) in self.current_dict.items():
                if v['quote'] == self.current_quote:
                    self.current_id = k
                    break
        else:
            with open(self.dict_file, mode="rt", encoding = "utf-8-sig") as f:
                self.prompt_list.clear()
                self.current_dict = json.load(f)
                self.quotes = {}
                for key, y in self.current_dict.items():
                    kwds = []
                    item = y['quote'].strip()
                    self.quotes[key]= item
                    self.prompt_list.append(item)
                completer = QCompleter(self.prompt_list)
                self._add_box.setCompleter(completer)
                self._quote_box.addItems(self.quotes.values())
                self.current_quote = self._quote_box.currentText()
            for (k, v) in self.current_dict.items():
                if v['quote'] == self.current_quote:
                    self.current_id = k
                    break                
                self._load_btn.setText("重载语料")

    def display_quote(self, quote):
        if self.current_dict:
            total = len(self.current_dict.keys())
            self.current_quote = quote
            for k, v in self.current_dict.items():
                if v['quote']== self.current_quote:
                    self.current_id = k
                    break            
            self._quote_box.setCurrentIndex(int(self.current_id)-1)
            self.show_data(self.current_dict, self.current_id, total)
            
    def display_data(self):
        self.reset_form()
        if self.current_dict:
            total = len(self.current_dict.keys())
            self.current_quote = self._quote_box.currentText()
            for k, v in self.current_dict.items():
                if v['quote']== self.current_quote:
                    self.current_id = k
                    break
            self.show_data(self.current_dict, self.current_id, total)
        else:
            self.set_status_text("数据库文件缺失，请重试！")
        
    def show_data(self, dt, i, t):
        quote = dt[i]["quote"]
        self._id_box.setText(i)
        self._source_box.setText(dt[i]['source'])
        alias = dt[i].get('alias',"")
        self._alias_box.setText(alias)
        self._origin_box.setText(dt[i]['origin'])
        self._meaning_box.setText(dt[i]['meaning'])
        self._date_box.setText(dt[i]['date'])
        self._category_box.setText(dt[i]['category'])
        self.setWindowTitle(f'引言语料编辑-辞条{i}/{t}')
        
    def update_data(self):
        new_dict = {}
        self.current_id = self._id_box.text()
        new_dict['quote'] = self._quote_box.currentText()
        new_dict['alias'] = self._alias_box.text()
        new_dict['source'] = self._source_box.text()        
        new_dict['origin'] = self._origin_box.toPlainText()
        new_dict['meaning'] = self._meaning_box.toPlainText()
        new_dict['date'] = self._date_box.text()
        new_dict['category'] = self._category_box.text()
        if self.current_id in self.current_dict.keys():
            self.current_dict[self.current_id].update(new_dict)
        else:
            self.current_dict[self.current_id]=new_dict
        self.set_status_text("当前辞条已更新！")
        
    def reset_form(self):
        self._id_box.clear()
        self._alias_box.clear()
        self._source_box.clear()        
        self._origin_box.clear()
        self._meaning_box.clear()
        self._date_box.clear()
        self._category_box.clear()
        self._add_box.clear()
        
    def add_data(self):
        new_item = self._add_box.text()
        new_id = str(len(self.current_dict)+1)
        if self.current_dict.get(new_id,""):
            self.set_status_text("当前辞条索引号已存在，请重试！")
        else:
            self.current_id = new_id
            self.reset_form()        
            new_dict = {}        
            if new_item in self.prompt_list:
                self.display_quote(new_item)
                self.set_status_text("当前辞条已存在！")                        
            else:
                new_dict['quote'] = new_item
                new_dict['alias'] = self._alias_box.text()
                new_dict['source'] = self._source_box.text()
                new_dict['origin'] = new_item
                new_dict['meaning'] = self._meaning_box.toPlainText()
                new_dict['date'] = self._date_box.text()
                new_dict['category'] = self._category_box.text()
            if new_dict:
                self.current_dict[new_id]=new_dict
                self.current_quote = new_item
                self.quotes[new_id]=new_dict
                self.set_status_text("当前辞条已创立！")
                self.prompt_list.append(new_item)
                self._quote_box.addItem(new_item)
                self._quote_box.setCurrentIndex(int(new_id)-1)
                self.reset_form()
                self.display_data()                

    def del_data(self):
        old_id = self.current_id
        old_quote = self.current_quote
        del self.current_dict[old_id]
        del self.quotes[old_id]
        self.prompt_list.remove(old_quote)
        self.current_id = '1'
        self.set_status_text("当前辞条已删除！")
        self.reset_form()
        self.load_data()
            
    def save_data(self):
        new_dict = {}
        for (k, v) in sorted(self.current_dict.items(), key = lambda k:int(k[0])):
            new_dict[k]=v
        self.write_to_json(new_dict)
    
    def write_to_json(self, data):
        with open(self.dict_file, 'wt', encoding='utf-8-sig')as f:
            json.dump(data, f)
            self.set_status_text("文件已保存！")
            
    def set_status_text(self, text):
        self._statusBar.showMessage(text, 3000)  

