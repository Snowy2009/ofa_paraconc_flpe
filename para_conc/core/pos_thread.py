#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import os, sys, json, re, time, copy
from collections import Counter, defaultdict
from PySide6.QtCore import Qt, QSize, QPoint, Signal, Slot, QThread
from para_conc.core.search.searchResultConverter import VocFreqResultConverter
    
class TagThread(QThread):
    pbar_signal = Signal([int, int]) 
    msg_m_signal = Signal(str)
    output_window_signal = Signal([str, str, str])
    def __init__(self, opt, stp_zh, stp_en, zh_dt, en_dt, lang): 
        super(TagThread, self).__init__()
        currentDir = os.getcwd()
        dataDir = os.path.join(currentDir, "app_data")
        workFileDir = os.path.join(dataDir, "workfiles")
        self.imgDir = os.path.join(dataDir, "images")
        self._outPutDir = os.path.join(currentDir, "saved_files")
        self.puncFile =  os.path.join(workFileDir, "punc.dat")
        self.puncs = []        
        
        self.acronyms = ['CPC', 'PS', 'IT', 'MPT', 'UN',
                         'GDP', 'MIT', 'ICT', 'TV', 'UK',
                         'UNESCO', 'MOE', 'BC', 'AD', 'III',
                         'II', 'EU', 'I', "III", "IV", "V",
                         "VI", "VII", "VIII", "IX", "X",
                         "XI", "XII", "AI", "Vol.", "p."]
        self._converter = VocFreqResultConverter()
        self.outdicts_zh = zh_dt
        self.outdicts_en = en_dt
        self.merged_dict_zh = {}
        self.merged_dict_en = {}
        self.stop_zh = stp_zh
        self.stop_en = stp_en
        self.filters = opt
        self.word_tag_list = []
        self.word_list = []
        self.lang = lang

        self.get_puncs()

    def __del__(self):
        pass
    
    def get_puncs(self):
        with open(self.puncFile, "rt", encoding="utf-8-sig") as f:
            self.puncs = [x.strip() for x in f.readlines()]
        return self.puncs
    
    def output_dict_merger(self, output_dict_list):
        output_dict = defaultdict(list) 
        merged_dict = defaultdict(list) 
        for ipd in output_dict_list:                    
            for key, values in ipd.items():           
                n_key = key[0]                         
                if n_key not in merged_dict.keys():     
                    merged_dict[n_key]=values
                else:                                  
                    md_dict = {}                        
                    for (m,d,q) in merged_dict[n_key]:  
                        if (m,d) not in md_dict.keys():
                            md_dict[(m,d)]=q          
                        else:
                            md_dict[(m,d)]+=q          
                    for (w,t,q) in values:             
                        if (w,t) not in md_dict.keys():
                            md_dict[(w,t)]=q            
                        else:
                            md_dict[(w,t)]+=q          
                    new_values = [(k,t,q) for (k,t),q in md_dict.items()] 
                    merged_dict[n_key]=new_values                         
        for k, v_list in merged_dict.items():   
            tn = sum([q for (w,t,q) in v_list])        
            output_dict[(k,tn)]=v_list                 
        return output_dict                            

    def item_remover(self, input_dict, target="punc"):
        output_dict = copy.deepcopy(input_dict)
        if target == "punc":
            for (w, q) in input_dict.keys():
                if w in self.puncs:
                    del output_dict[(w,q)]
            return output_dict
        elif target == "arab":
            reg = r"([0-9\.\,-]+)"
            for (w, q) in input_dict.keys():
                r = re.search(reg, w)
                if r:
                    tag = ""
                    for (wd, tg, fq) in input_dict[(w,q)]:
                        if tg == "CD" or tg =="m":
                            tag = "arab"
                            break
                    if tag:
                        del output_dict[(w,q)]
            return output_dict
        elif target == "z_alien":
            reg = r'[a-zA-Z]+'
            for (w, q) in input_dict.keys():
                r = re.search(reg, w)
                if r:
                    del output_dict[(w,q)]
            return output_dict
        else:
            return output_dict
            
    def off_item_remover(self, my_dict, opt_dict, lang = "en"):
        off_list = opt_dict.get('off',[])
        if off_list:            
            if lang == "zh":
                clean_dict = copy.deepcopy(my_dict)
                if 'z_punc' in off_list:
                    clean_dict = self.item_remover(clean_dict, target="punc")
                if 'z_arab' in off_list:
                    clean_dict = self.item_remover(clean_dict, target="arab")
                if 'z_alien' in off_list:
                    clean_dict = self.item_remover(clean_dict, target="z_alien")
                return clean_dict
            else:
                clean_dict = copy.deepcopy(my_dict)
                if 'e_punc' in off_list:
                    clean_dict = self.item_remover(clean_dict, target="punc")
                if 'e_arab' in off_list:
                    clean_dict = self.item_remover(clean_dict, target="arab")
                return clean_dict                
        else:
            return my_dict
        
    def dict_filter(self, my_dict, word_list, freq, length):
        new_dict ={}                
        for (w, q) in my_dict.keys():            
            if w.title() not in word_list and w.lower() not in word_list and int(q) >= int(freq) and len(w) >= int(length):
                new_dict[(w,q)]= copy.deepcopy(my_dict[(w,q)])
        return new_dict
    
    def result_list_generator(self, final_dict, lang = "zh"):        
        if lang == "zh":
            result_list_zh = []
            nm_list_zh = []
            hw_list_zh = []
            hq_list_zh = []
            tq_list_zh =[]
            for i, (w,q) in enumerate(sorted(final_dict.keys(), key=lambda x:x[1],reverse =True),start=1):
                st_list = [w+ "/"+q + " ("+str(f)+")" for w, q, f in final_dict[(w,q)]]
                st = "; ".join(st_list)             
                nm_list_zh.append(str(i))
                hw_list_zh.append(w)
                hq_list_zh.append(q)
                tq_list_zh.append(st)
            return nm_list_zh, hw_list_zh, hq_list_zh, tq_list_zh
        else:
            result_list_en = []
            nm_list_en = []
            hw_list_en = []
            hq_list_en = []
            tq_list_en =[]
            for i, (w,q) in enumerate(sorted(final_dict.keys(), key=lambda x:x[1],reverse =True),start=1):
                st_list = [w+ "_"+q + " ("+str(f)+")" for w, q, f in final_dict[(w,q)]]
                st = "; ".join(st_list)
                nm_list_en.append(str(i))
                hw_list_en.append(w)
                hq_list_en.append(q)
                tq_list_en.append(st)
            return nm_list_en, hw_list_en, hq_list_en, tq_list_en
        
    def run (self): 
        T1 = time.perf_counter()
        self.msg_m_signal.emit("正在为您准备词表，请稍候....")
        self.pbar_signal.emit(1,10)
        time.sleep(2)
        self.pbar_signal.emit(2,10)
        if self.lang == "zh":
            self.msg_m_signal.emit("开始获取所选语料中文词典列表，请稍候....")
            self.merged_dict_zh = self.output_dict_merger(self.outdicts_zh)
            self.pbar_signal.emit(3,10)
            if self.merged_dict_zh:
                self.pbar_signal.emit(4,10)
                self.msg_m_signal.emit("正在检查中文词频过滤设置，请稍候....")
                self.off_clean_dict_zh = self.off_item_remover(self.merged_dict_zh, self.filters, "zh")
                if "z_stop" in self.filters['stop']:
                    stop_list = self.stop_zh
                else:
                    stop_list = []
                zh_freq = self.filters['freq']["zh"]
                zh_length = self.filters['length']["zh"]
                final_zh_dict = self.dict_filter(self.off_clean_dict_zh, stop_list, zh_freq, zh_length)
                self.pbar_signal.emit(5,10)
                self.msg_m_signal.emit("正在转换中文词频列表格式，请稍候....")
                word_tag_result_list =[]
                if final_zh_dict:
                    nm_list_zh, hw_list_zh, hq_list_zh, tq_list_zh = self.result_list_generator(final_zh_dict, "zh")
                    self.pbar_signal.emit(6,10) 
                    result_pd_zh = self._converter.lst2pd(nm_list_zh, hw_list_zh, hq_list_zh, tq_list_zh)
                    voc_html_zh = self._converter.pd2html(result_pd_zh)
                    voc_txt_zh = "\n".join([str(a)+ "\t" +b + "\t" + str(c) + "\t" +d for (a,b,c,d) in zip(nm_list_zh, hw_list_zh,hq_list_zh,tq_list_zh)])
                    if voc_html_zh:
                        self.pbar_signal.emit(7,10)
                        self.msg_m_signal.emit("正在打印中文词频列表，请稍候....")
                        task_title = f"中文词汇词性与词频列表"
                        task_file = voc_html_zh
                        self.output_window_signal.emit(task_title, task_file, self.lang)
                        self.pbar_signal.emit(8,10)
                        self.msg_m_signal.emit("正在保存中文词频列表到本地，请稍候....")
                        zh_html_to_save = os.path.join(self._outPutDir, "word_tag_freq_zh_result.html")
                        zh_txt_to_save = os.path.join(self._outPutDir, "word_tag_freq_zh_result.txt")
                        with open(zh_html_to_save, 'w', encoding="utf-8-sig") as f:
                            f.write(voc_html_zh)
                        with open(zh_txt_to_save, 'wt', encoding="utf-8-sig") as f:
                            f.write(voc_txt_zh)
                        self.pbar_signal.emit(9,10)
                        self.msg_m_signal.emit("中文词频列表已保存到本地")
                        T2 = time.perf_counter()
                        time_used = T2 - T1
                        self.pbar_signal.emit(10,10)
                        self.msg_m_signal.emit(f"中文词表处理完毕，共用时{time_used:.2f}秒")
                    else:
                        T2 = time.perf_counter()
                        time_used = T2 - T1
                        self.pbar_signal.emit(10,10)
                        self.msg_m_signal.emit(f"抱歉，准备工作出错，请联系软件维护人员，本次共用时{time_used:.2f}秒")
                else:
                    T2 = time.perf_counter()
                    time_used = T2 - T1
                    self.pbar_signal.emit(10,10)
                    self.msg_m_signal.emit(f"抱歉，准备工作出错，请联系软件维护人员，本次共用时{time_used:.2f}秒")
            time.sleep(1)
            self.pbar_signal.emit(-1,10)                        
        else:
            self.msg_m_signal.emit("开始获取所选语料英文分词列表，请稍候....")
            self.merged_dict_en = self.output_dict_merger(self.outdicts_en)
            self.pbar_signal.emit(3,10)
            if self.merged_dict_en:
                self.pbar_signal.emit(4,10)
                self.msg_m_signal.emit("正在检查英文词频过滤设置，请稍候....")
                self.off_clean_dict_en = self.off_item_remover(self.merged_dict_en, self.filters)
                if "e_stop" in self.filters['stop']:
                    stop_list = self.stop_en
                else:
                    stop_list = []
                en_freq = self.filters['freq']["en"]
                en_length = self.filters['length']["en"]
                final_en_dict = self.dict_filter(self.off_clean_dict_en, stop_list, en_freq, en_length)
                self.pbar_signal.emit(5,10)
                self.msg_m_signal.emit("正在转换英文词频列表格式，请稍候....")
                word_tag_result_list =[]
                if final_en_dict: 
                    nm_list_en, hw_list_en, hq_list_en, tq_list_en = self.result_list_generator(final_en_dict, "en")            
                    self.pbar_signal.emit(6,10) 
                    result_pd_en = self._converter.lst2pd(nm_list_en, hw_list_en, hq_list_en, tq_list_en)                
                    voc_html_en = self._converter.pd2html(result_pd_en)
                    voc_txt_en = "\n".join([str(a)+ "\t" +b + "\t" + str(c) + "\t" +d for (a,b,c,d) in zip(nm_list_en, hw_list_en,hq_list_en,tq_list_en)])
                    if voc_html_en:
                        self.pbar_signal.emit(7,10)
                        self.msg_m_signal.emit("正在打印英文词频列表，请稍候....")
                        task_title = f"英文词汇词性与词频列表"
                        task_file = voc_html_en
                        self.output_window_signal.emit(task_title, task_file, self.lang)
                        self.pbar_signal.emit(8,10)
                        self.msg_m_signal.emit("正在保存中文词频列表到本地，请稍候....")
                        en_html_to_save = os.path.join(self._outPutDir, "word_tag_freq_en_result.html")
                        en_txt_to_save = os.path.join(self._outPutDir, "word_tag_freq_en_result.txt")
                        with open(en_html_to_save, 'w', encoding="utf-8-sig") as f:
                            f.write(voc_html_en)
                        with open(en_txt_to_save, 'wt', encoding="utf-8-sig") as f:
                            f.write(voc_txt_en)
                        self.pbar_signal.emit(9,10)
                        self.msg_m_signal.emit("英文词频列表已保存到本地")
                        T2 = time.perf_counter()
                        time_used = T2 - T1
                        self.pbar_signal.emit(10,10)
                        self.msg_m_signal.emit(f"英文词表处理完毕，共用时{time_used:.2f}秒")
                    else:
                        T2 = time.perf_counter()
                        time_used = T2 - T1
                        self.pbar_signal.emit(10,10)
                        self.msg_m_signal.emit(f"抱歉，准备工作出错，请联系软件维护人员，本次共用时{time_used:.2f}秒")                        
                else:
                    T2 = time.perf_counter()
                    time_used = T2 - T1
                    self.pbar_signal.emit(10,10)
                    self.msg_m_signal.emit(f"抱歉，准备工作出错，请联系软件维护人员，本次共用时{time_used:.2f}秒")              
            time.sleep(1)
            self.pbar_signal.emit(-1,10)          
