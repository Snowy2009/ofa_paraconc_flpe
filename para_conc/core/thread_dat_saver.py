#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import os, sys, time, json, pickle
from PySide6.QtCore import Signal, Slot, QThread
from para_conc.core.CorpusGeneral import GenCorpus
from para_conc.core.CorpusEDU import EduCorpus

class DatSaverThread(QThread):
    pbar_signal = Signal([int, int]) 
    msg_m_signal = Signal(str)       
    output_window_signal = Signal([str, str, str])
    refresh_signal = Signal(list)    
    def __init__(self, dict_list):   
        super(DatSaverThread, self).__init__()
        self._currentDir = os.getcwd()
        self._dataDir = os.path.join(self._currentDir, "app_data")  
        self._datFileDir = os.path.join(self._dataDir, "temp_data")
        self._savedFiles = [os.path.join(self._datFileDir,x) for x in os.listdir(self._datFileDir)]
        self._errorLog = os.path.join(self._dataDir, "data_error_log.txt")
        self.files_to_handle = dict_list 
        self.new_corpora = []            

    def __del__(self):
        pass
      
    def open_json_file(self, json_file):
        json_read = ''
        with open(json_file, 'rb') as f:
            json_read = json.load(f)
        return json_read
    
    def run (self): 
        T1 = time.perf_counter()        
        self.msg_m_signal.emit("语料读取中，请稍候....")
        j = len(self.files_to_handle)
        self.pbar_signal.emit(0,j)
        time.sleep(2)
        for i, (c_file, c_id) in enumerate(self.files_to_handle, start = 1):
            check_id = os.path.join(self._datFileDir, c_id+".dat")
            if check_id in self._savedFiles:                
                pass
            else:
                c_dict = self.open_json_file(c_file)
                corpera_item = ""
                if c_dict['genre'][1] in ["new year address","signed article abroad",\
                                          "speech at home and abroad","white paper",\
                                          "government work report", "report to national congress"]:
                    corpera_item = GenCorpus()                     
                elif c_dict['genre'][1] == "governance of china":
                    corpera_item = GocCorpus()
                elif c_dict['genre'][1] == "educational philosophy":
                    corpera_item = EduCorpus()
                else: pass
                if corpera_item:
                    self.msg_m_signal.emit("开始生成语料，请稍候....")
                    corpera_item.generate_corpus(c_dict)                
                    corpera_item.id = c_id
                    if c_dict['genre'][1] == "educational philosophy":
                        self.pbar_signal.emit(1,5)
                        self.msg_m_signal.emit("开始获取章节，请稍候....")
                        corpera_item.get_articles(c_dict)
                        self.pbar_signal.emit(2,5)
                        self.msg_m_signal.emit("开始更新注释，请稍候....")
                        corpera_item.copy_notes()
                        self.pbar_signal.emit(3,5)
                        self.msg_m_signal.emit("开始统计各章节语料，请稍候....")
                        corpera_item.calculating_articles()
                        self.pbar_signal.emit(4,5)
                        self.msg_m_signal.emit("开始计算英文类形比，请稍候....")
                        corpera_item.update_ratio()
                        self.pbar_signal.emit(5,5)
                        self.msg_m_signal.emit(f"语料{i}统计完毕")                        
                    else:
                        self.pbar_signal.emit(1,5)
                        self.msg_m_signal.emit("开始生成词性列表，请稍候....")
                        corpera_item.get_word_tag_list()
                        self.pbar_signal.emit(2,5)
                        self.msg_m_signal.emit("开始生成词频，请稍候....")
                        corpera_item.get_freq_dict()
                        self.pbar_signal.emit(3,5)
                        self.msg_m_signal.emit("开始生成词频字典，请稍候....")
                        corpera_item.get_output_dict()
                        self.pbar_signal.emit(4,5)
                        self.msg_m_signal.emit("开始计算英文类形比，请稍候....")
                        corpera_item.get_en_sttr()
                        self.pbar_signal.emit(5,5)
                        self.msg_m_signal.emit("开始计算英文类形比，请稍候....")
                        self.msg_m_signal.emit(f"语料{i}统计完毕")
                    self.pbar_signal.emit(i,j)
                    if corpera_item.warnings:
                        with open (self._errorLog, "a+", encoding="utf-8-sig") as f:
                            f.write(c_id+"\n"+"\n".join(corpera_item.warnings)+"="*30+"\n")
                        new_id = c_id+".dat" 
                        pkl_to_save = os.path.join(self._datFileDir, new_id)                    
                        with open (pkl_to_save, 'wb') as f:
                            pickle.dump(corpera_item, f)
                        self.new_corpora.append((pkl_to_save, c_id)) 
                        self.msg_m_signal.emit(f"{c_id}的语料文件保存成功")
                        time.sleep(1)
                    else:
                        new_id = c_id+".dat"
                        pkl_to_save = os.path.join(self._datFileDir, new_id)                    
                        with open (pkl_to_save, 'wb') as f:
                            pickle.dump(corpera_item, f)
                        self.new_corpora.append((pkl_to_save, c_id)) 
                        self.msg_m_signal.emit(f"{c_id}的语料文件保存成功")
                        time.sleep(1)
                else:
                    msg = f"{c_id}JSON语料文件未指定体裁类型，DAT转写失败"
                    self.msg_m_signal.emit(msg)            
                    self.pbar_signal.emit(i,j) 
                
        T2 = time.perf_counter()
        time_used = T2 - T1
        self.msg_m_signal.emit(f"已成功转写{j}个语料文件，共用时{time_used:.2f}秒")
        if self.new_corpora:
            self.refresh_signal.emit(self.new_corpora)
        time.sleep(1)
        self.pbar_signal.emit(-1,10) 
