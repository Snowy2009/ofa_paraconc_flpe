#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import os, sys, json, re, time, copy, codecs, pickle
from collections import Counter, defaultdict
from PySide6.QtCore import Qt, QSize, QPoint, Signal, Slot, QThread
from wordcloud import WordCloud
from imageio import imread
    
class CloudThread(QThread):
    obj_signal = Signal(dict)
    pbar_signal = Signal([int, int]) 
    msg_m_signal = Signal(str)
    output_window_signal = Signal([str, str, str])
    def __init__(self, opt, stp_zh, stp_en, zh_dict, en_dict): 
        super(CloudThread, self).__init__()
        currentDir = os.getcwd()
        dataDir = os.path.join(currentDir, "app_data")
        imgDir = os.path.join(dataDir, "images")
        fontDir = os.path.join(dataDir, "fonts")
        workFileDir = os.path.join(dataDir, "workfiles")
        self._maskDir = os.path.join(imgDir,"cloud_modules")
        self.font_path = os.path.join(fontDir, "simhei.ttf")
        self._outPutDir = os.path.join(currentDir, "saved_files")

        self._img_carrier = {}            
        self.msg = ""
        self.stop_zh = stp_zh                
        self.stop_en = stp_en 
        self.stop_bi = stp_zh + stp_en        
        self.lang = opt['lang']              
        self.stop_tags = opt['tag']                               
        self.stop_switch = opt['stop_list']
        self.stop_words = []          
        self.wtf_dict = {}
        
        if self.lang == "zh":
            if self.stop_switch == 'on':            
                self.stop_words = self.stop_zh 
            self.wtf_dict = zh_dict
        elif self.lang == "en":
            if self.stop_switch == 'on':
                self.stop_words = self.stop_en
            self.wtf_dict = en_dict
        elif self.lang == "bi":
            if self.stop_switch == 'on':
                self.stop_words = self.stop_bi
            self.wtf_dict = zh_dict
            self.wtf_dict.update(en_dict)
        else:
            pass
        self.length_min = opt['length']
        self.freq_min = opt['freq']
        self.font_min = opt['font_min']
        self.font_max = opt['font_max']
        self.word_max = opt['word_max']
        self.color_mode = opt['mode']
        self.color_random = opt['random']
        self.color_bg = opt['bg_color']
        self.color_func = opt['wd_color']        
        self.color_mask = None
        self.mask_id = opt['mask']
        if self.mask_id != None:
            mask_string = self.mask_id+".png"
            mask_img = os.path.join(self._maskDir, mask_string)
            self.color_mask = imread(mask_img) 
            
    def draw_cloud(self):
        voc_dict = {}
        for (w,q),lemma in self.wtf_dict.items():
            if len(w) >= self.length_min and q >= self.freq_min and \
               w not in self.stop_words and lemma[0][1][0] not in self.stop_tags:
                voc_dict[w]=q
        if self.color_func == None:
            cloud = WordCloud(            
                font_path=self.font_path,        
                background_color=self.color_bg, 
                color_func = None,
                mask=self.color_mask,                           
                max_words=self.word_max,                         
                max_font_size=self.font_max,                        
                min_font_size=self.font_min,                    
                random_state=self.color_random,                  
                stopwords=None,                 
                mode=self.color_mode,    
                )
        else:
            cloud = WordCloud(            
                font_path=self.font_path,           
                background_color=self.color_bg, 
                color_func = lambda *args, **kwargs: self.color_func, 
                mask=self.color_mask,                           
                max_words=self.word_max,                          
                max_font_size=self.font_max,                        
                min_font_size=self.font_min,                          
                random_state=self.color_random,                    
                stopwords=None,          
                mode=self.color_mode,    
                )        
        word_cloud = cloud.generate_from_frequencies(voc_dict)
        current_img_carrier = {}
        current_img_carrier["word_cloud"]=word_cloud
        msg= f"词云图已生成!"
        return current_img_carrier, msg

        
    def __del__(self):
        pass
        
    def run (self): 
        T1 = time.perf_counter()
        self._current_img_carrier = ""
        self.msg_m_signal.emit("开始生成词云，请稍候....")
        self.pbar_signal.emit(1,3)
        time.sleep(2)
        self.pbar_signal.emit(2,3)
        self.current_img_carrier, self.msg = self.draw_cloud()
        if self.msg:
            self.pbar_signal.emit(3,3)
            T2 = time.perf_counter()
            time_used = T2 - T1
            self.msg_m_signal.emit(f"词云已生成，共用时{time_used:.2f}秒")
            self.obj_signal.emit(self.current_img_carrier)
            time.sleep(1)            
            self.pbar_signal.emit(-1,3)                        
        else:
            T2 = time.perf_counter()
            time_used = T2 - T1
            self.pbar_signal.emit(10,10)
            self.msg_m_signal.emit(f"词云绘制失败，请重试，本次共用时{time_used:.2f}秒")
            time.sleep(1)
            self.pbar_signal.emit(-1,3)
