#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import re, copy, json
from collections import Counter, defaultdict
from para_conc.core.statistics import Statistics
   
class Note:
    def __init__(self):
        self.num = 0          
        self.index = ""       
        self.index_tag = ""   
        self.note = ""        
        self.note_tag = ""    
        self.sent_count = 0
        self.seg_count = 0
        self.raw_text = ""  
        self.tag_text = ""          

class Sent:
    def __init__(self):
        self.num = 0  
        self.zh = ""     
        self.en = ""        
        self.zh_tag = "" 
        self.en_tag = "" 
        self.zh_sent_count = 0
        self.zh_seg_count = 0
        self.en_sent_count = 0
        self.en_seg_count = 0
        # self.zh_sent_length = 0 
        # self.en_sent_length = 0 
        self.bi_sent_ratio = ""
        self.bi_seg_ratio = ""        
   
class Para:
    def __init__(self): 
        self.num = 0      
        self.sents = []    
        self.bi_sent_count = 0
        self.zh_para_count = 0 
        self.en_para_count = 0 
        self.zh_sent_count = 0
        self.en_sent_count = 0
        self.zh_seg_count = 0
        self.en_seg_count = 0
        self.bi_para_ratio = 0
        self.bi_sent_ratio = 0
        self.bi_seg_ratio = 0
        self.raw_text_zh = "" 
        self.raw_text_en = "" 
        self.tag_text_zh = "" 
        self.tag_text_en = "" 

class GenCorpus:
    def __init__(self):        
        self.id = ""
        self.type_zh = ""        
        self.type_en = ""        
        self.genre_zh = ""
        self.genre_en = ""
        self.title_zh = ""     
        self.title_en = ""
        self.author_zh = ""     
        self.author_en = ""
        self.date_zh = ""         
        self.date_en = ""
        self.place_zh = ""          
        self.place_en = ""
        self.source_zh = ""     
        self.source_en = ""
        self.background_zh = ""    
        self.background_en = ""   
        self.paras = []          
        self.notes_zh = []       
        self.notes_en = []
        self.notes_title_zh = "" 
        self.notes_title_en = ""  
        self.notes_title_zh_tag = "" 
        self.notes_title_en_tag = ""
        self.raw_text_zh = ""
        self.raw_text_en = ""
        self.tag_text_zh = ""
        self.tag_text_en = ""        
       
        self.bi_para_count = 0    
        self.bi_sent_count = 0    
        self.bi_para_ratio = 0    
        self.bi_sent_ratio = 0   
        self.bi_seg_ratio = 0    
        self.zh_para_count = 0   
        self.en_para_count = 0   
        self.zh_sent_count = 0   
        self.en_sent_count = 0   
        self.zh_seg_count = 0   
        self.en_seg_count = 0   

        self.zh_token_tag_list = []
        self.en_token_tag_list = []
        self.zh_token_tag_freq = {} 
        self.en_token_tag_freq = {}
        
        self.zh_word_tag_list = []
        self.en_word_tag_list = []        
        self.zh_word_tag_freq = {} 
        self.en_word_tag_freq = {}
        self.en_word_tag_freq_list = []
        
        self.zh_token_output_dict = defaultdict(dict)
        self.en_token_output_dict = defaultdict(dict)
        self.zh_word_output_dict = defaultdict(dict)
        self.en_word_output_dict = defaultdict(dict)
        
        self.zh_byte_count = 0
        self.en_byte_count = 0
        self.zh_token_count = 0
        self.en_token_count = 0
        self.zh_type_count = 0
        self.en_type_count = 0        
        self.zh_word_token_count = 0
        self.en_word_token_count = 0                
        self.zh_word_type_count = 0
        self.en_word_type_count = 0
        
        self.zh_word_ttr = 0
        self.en_word_ttr = 0        
        self.zh_word_sttr = 0
        self.en_word_sttr = 0

        self.warnings = []

        self.dat = Statistics()        
   
    def get_notes(self, my_dict):
        notes_title = my_dict['notes'].get("title","")
        notes_title_tag = my_dict['notes'].get("title_tag","")
        zh_notes = my_dict['notes'].get("zh","")
        zh_notes_tag = my_dict['notes'].get("zh_tag","")
        en_notes = my_dict['notes'].get("en","")
        en_notes_tag = my_dict['notes'].get("en_tag","")
        invalid_regex = r"[〔\[](无|None|NONE|UnTr)[\]〕]"
        if notes_title and notes_title_tag:
            self.notes_title_zh = notes_title[0]
            self.notes_title_en = notes_title[1]
            self.notes_title_zh_tag = notes_title_tag[0]
            self.notes_title_en_tag = notes_title_tag[1]
        if zh_notes or en_notes:
            if zh_notes and zh_notes_tag:                
                for i,((k, v),(kg,vg)) in enumerate(zip(zh_notes.items(),zh_notes_tag.items()),start=1):
                    r = re.search(invalid_regex, v)
                    if not r:
                        new_note = Note() 
                        new_note.num = i
                        new_note.index = k
                        new_note.index_tag = kg
                        if k == "*":
                            new_note.index = k
                            new_note.index_tag = kg+"/w"
                        new_note.note = v
                        new_note.note_tag = vg
                        new_note.sent_count, new_note.seg_count = self.seg_finder(v, 'zh')
                        new_note.para_count = 1 + v.count("[PS]") 
                        new_note.raw_text = new_note.index + "" + new_note.note
                        new_note.tag_text = new_note.index_tag + " " + new_note.note_tag
                        self.notes_zh.append(new_note)
            if en_notes and en_notes_tag:
                for j,((k, v),(kg,vg)) in enumerate(zip(en_notes.items(),en_notes_tag.items()),start=1):
                    r = re.search(invalid_regex, v)
                    if not r:
                        new_note = Note() 
                        new_note.num = j
                        new_note.index = k
                        new_note.index_tag = kg
                        if k == "*":
                            new_note.index = k
                            new_note.index_tag = kg
                        new_note.note = v
                        new_note.note_tag = vg
                        new_note.sent_count, new_note.seg_count = self.seg_finder(v, 'en')
                        new_note.para_count = 1 + v.count("[PS]") 
                        new_note.raw_text = new_note.index + "" + new_note.note
                        new_note.tag_text = new_note.index_tag + " " + new_note.note_tag
                        self.notes_en.append(new_note)
             
    def get_info(self, data):
        self.type_zh = data['type'][0]
        self.type_en = data['type'][1]
        self.genre_zh = data['genre'][0]
        self.genre_en = data['genre'][1]
        self.title_zh = data['title'][0]    
        self.title_en = data['title'][1]    
        self.author_zh = data['author'][0]  
        self.author_en = data['author'][1]  
        self.date_zh = data['date'][0]      
        self.date_en = data['date'][1]      
        self.place_zh = data['place'][0]    
        self.place_en = data['place'][1]    
        self.source_zh = data['source'][0]
        self.source_en = data['source'][1]
        self.background_zh = data['background'][0] 
        self.background_en = data['background'][1]
        
    def seg_finder(self, sent, lang="zh"):
        punc_regex = r"[\[〔。，？！；…“”—\.\,\?\!\;:\-\'\"]"
        en_seg_regex = r"[\,\;\:\-\"\']+\s+"
        zh_seg_regex = "[，—：；、]+" 
        sent_num = 0
        seg_num = 0
        s = re.search(punc_regex, sent)
        if not s:               
            sent_num += 1        
            seg_num += 1          
        elif lang == "zh":        
            para = re.sub(r'\[PS\]', r"\n", sent) 
            para = re.sub('([。！？\?][。！？\?])', r"\1\n", para) 
            para = re.sub('([。！？\?][”’）])', r"\1\n", para)
            para = re.sub('([”’）][”’）])', r"\1\n", para)
            para = re.sub('([。！？\?])([^”’）])', r"\1\n\2", para) 
            para = re.sub('(\w)([：；])(\w)', r"\1\2\n\3", para) 
            para = re.sub('(\.{6})([^”’）])', r"\1\n\2", para)  
            para = re.sub('(\…{2})([^”’）])', r"\1\n\2", para) 
            para = re.sub('([。！？\?][”’）])([^，。！？\?])', r'\1\n\2', para)
            para = re.sub('([！？\?，。])(\n)([！？\?，。])', r'\1\3', para)
            para = re.sub('\ufeff', r"", para) 
            para = re.sub('\n\n', r"\n", para)
            para = re.sub('\n(〔\d+〕)', r'\1\n', para)
            para = para.rstrip()
            para_sents=para.split("\n")
            sents= [x.strip() for x in para_sents if x.strip() and x.lstrip().rstrip() != '〔无〕' ]
            sent_num += len(sents)
            for st in sents:
                segs = [z for z in re.split(zh_seg_regex, st) if z.strip()!=""]
                seg_num += len(segs)
        elif lang == "en":            
            para = re.sub(r'\[PS\]', r"\n", sent)
            para = re.sub('(;’|;|;"|;”) ', r"\1\n", para)
            para = re.sub('(\.) ', r"\1\n", para)
            para = re.sub('(\?|\?\'|\?"|\?”)\s+([A-Z“‘]) ', r"\1\n\2", para)
            para = re.sub('([’”])\s+([‘“])', r"\1\n\2", para)
            para = re.sub('(,”|,"|,\'|,’)\n', r"\1 ", para)
            para = re.sub('(Mr\.|Mrs.)\n', r"\1 ", para)
            para = re.sub('([A-Z]\.)\n([A-Z]\.)\n([A-Z])', r"\1 \2 \3", para)
            para = re.sub('(\.)\n(\.)\n(\.\n)', r"\1\2\3", para)
            para = re.sub('(\s[A-Z]\.|[\n“\"\'][A-Z]\.)\n([A-Z])', r"\1 \2", para)
            para = re.sub('(\.”)\s+([A-Z])', r"\1\n\2", para)            
            sents= [y.strip() for y in para.split("\n") if y.strip()!="" and y.lstrip().rstrip() != '[UnTr]']
            sent_num += len(sents)
            for st in sents:
                segs = [z for z in re.split(en_seg_regex, st) if z.strip()!=""]
                seg_num += len(segs)
        else:
            pass
        return sent_num, seg_num
        
    def get_paras(self, data):
        self.bi_para_count = len(data['paras'])     
        for num_key in data['paras']:
            raw_data = data['paras'][num_key]['raw']
            tag_data = data['paras'][num_key]['tag']
            gen_pa = Para()
            gen_pa.num = num_key
            zh_para_count = 1 + raw_data[0].count("[PS]") 
            en_para_count = 1 + raw_data[1].count("[PS]")
            zh_test = re.sub(r"\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]\s*","", raw_data[0]) 
            if zh_test.lstrip().startswith("|[PS]") or zh_test.lstrip().startswith("| [PS]") or zh_test.lstrip().startswith("[PS]"):
                zh_para_count -= 1                                   
            zh_test = re.sub(r"(\s*\|\s*|\s*\[PS\]\s*)","", zh_test) 
            if not zh_test.lstrip().rstrip():                          
                zh_para_count -= 1
            zh_para_count -= raw_data[0].count("|[PS][无]|[PS]") 
            zh_para_count -= raw_data[0].count("|[PS]〔无〕|[PS]")
            en_test = re.sub(r"\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]\s*","", raw_data[1])
            if en_test.lstrip().startswith("|[PS]") or en_test.lstrip().startswith("| [PS]")or en_test.lstrip().startswith("[PS]"):
                en_para_count -= 1
            en_test = re.sub(r"(\s*\|\s*|\s*\[PS\]\s*)","", en_test)
            if not en_test.lstrip().rstrip():
                en_para_count -= 1            
            en_para_count -= raw_data[1].count("|[PS][UnTr]|[PS]")
            en_para_count -= raw_data[1].count("| [PS][UnTr] | [PS]")
            gen_pa.zh_para_count = zh_para_count 
            gen_pa.en_para_count = en_para_count
            pa_zh = [x for x in raw_data[0].split("|") if x.strip()]
            pa_zht = [a for a in tag_data[0].split("|/xn ") if a.strip()]
            pa_en = [y for y in raw_data[1].split("|") if y.strip()]
            pa_ent = [b for b in tag_data[1].split("|_XN ") if b.strip()]
            if len(pa_zh) == len(pa_en) == len(pa_zht) == len(pa_ent):
                self.bi_sent_count += len(pa_zh) 
                gen_pa.bi_sent_count = len(pa_zh)
            else:
                self.warnings.append(f"Critical Error Occurred in file {self.title_zh}: bi sents are not aligned!\nzh_raw: {len(pa_zh)}, en_raw: {len(pa_en)}, zh_tag: {len(pa_zht)}, en_tag: {len(pa_ent)}")
                break
            for j, (zs, es, zt, et) in enumerate(zip(pa_zh, pa_en, pa_zht, pa_ent),start = 1):
                gen_st = Sent()
                gen_st.num = j
                gen_st.zh = zs.lstrip().rstrip()
                gen_st.zh_tag = zt.lstrip().rstrip()
                gen_st.en = es.lstrip().rstrip()
                gen_st.en_tag = et.lstrip().rstrip()                
                gen_st.zh_sent_count, gen_st.zh_seg_count = self.seg_finder(gen_st.zh, lang="zh")
                gen_st.en_sent_count, gen_st.en_seg_count = self.seg_finder(gen_st.en, lang="en") 
                gen_pa.zh_sent_count += gen_st.zh_sent_count
                gen_pa.en_sent_count += gen_st.en_sent_count
                gen_pa.zh_seg_count += gen_st.zh_seg_count
                gen_pa.en_seg_count += gen_st.en_seg_count                
                gen_st.bi_sent_ratio = f"{gen_st.zh_sent_count}:{gen_st.en_sent_count}" 
                gen_st.bi_seg_ratio = f"{gen_st.zh_seg_count}:{gen_st.en_seg_count}"
                gen_pa.sents.append(gen_st) 
            gen_pa.raw_text_zh = "".join([st.zh for st in gen_pa.sents if st.zh != "〔无〕" and st.zh != "[无]"])
            gen_pa.raw_text_en = " ".join([st.en for st in gen_pa.sents if st.en not in ["[None]", "[UnTr]", "[NONE]"]])
            gen_pa.tag_text_zh = " ".join([st.zh_tag for st in gen_pa.sents if st.zh_tag != "〔无〕/xw" and st.zh != "[无]/xw"])
            gen_pa.tag_text_en = " ".join([st.en_tag for st in gen_pa.sents if st.en_tag not in ["[None]_XW", "[UnTr]_XW", "[NONE]_XW"]])
            gen_pa.bi_para_ratio = self.get_ratio(gen_pa.zh_para_count, gen_pa.en_para_count) 
            gen_pa.bi_sent_ratio = self.get_ratio(gen_pa.zh_sent_count, gen_pa.en_sent_count) 
            gen_pa.bi_seg_ratio = self.get_ratio(gen_pa.zh_seg_count, gen_pa.en_seg_count)       
            self.paras.append(gen_pa)

    def get_ratio(self, zh_count, en_count):
        try:
            if en_count == 0 or zh_count == 0: 
                bi_ratio_result = f"{zh_count}:{en_count}"
            else: 
                bi_ratio = en_count / zh_count
                bi_ratio_result = f"1:{bi_ratio:.2f}"
                if bi_ratio_result.endswith(".00"):
                    bi_ratio_result = bi_ratio_result[:-3] 
                elif "." in bi_ratio_result and bi_ratio_result.endswith('0'):
                    bi_ratio_result = bi_ratio_result[:-1] 
                else:
                    pass                    
        except:
            bi_ratio_result = 0
            self.warnings.append(f"Warning: Critical zero error occured while getting sent and seg ratio")
        return bi_ratio_result

    def get_text(self):
        for para in self.paras:
            if not self.raw_text_zh:
                self.raw_text_zh = para.raw_text_zh.lstrip().rstrip()
            else:
                self.raw_text_zh += "\n"+para.raw_text_zh.lstrip().rstrip()
            if not self.raw_text_en:
                self.raw_text_en = para.raw_text_en.lstrip().rstrip()
            else:
                self.raw_text_en += "\n"+para.raw_text_en.lstrip().rstrip()
            if not self.tag_text_zh:
                self.tag_text_zh = para.tag_text_zh.lstrip().rstrip()
            else:
                self.tag_text_zh += "\n"+para.tag_text_zh.lstrip().rstrip()
            if not self.tag_text_en:
                self.tag_text_en = para.tag_text_en.lstrip().rstrip()
            else:
                self.tag_text_en += "\n"+para.tag_text_en.lstrip().rstrip()   
            self.zh_para_count += para.zh_para_count
            self.en_para_count += para.en_para_count
            self.zh_sent_count += para.zh_sent_count
            self.zh_seg_count += para.zh_seg_count
            self.en_sent_count += para.en_sent_count
            self.en_seg_count += para.en_seg_count

        self.raw_text_zh = self.clear_untr_marker(self.raw_text_zh, "r-z")
        self.raw_text_en = self.clear_untr_marker(self.raw_text_en, "r-e")
        self.tag_text_zh = self.clear_untr_marker(self.tag_text_zh, "t-z")
        self.tag_text_en = self.clear_untr_marker(self.tag_text_en, "t-e")

        actual_para_num_zh =len(self.raw_text_zh.split('\n'))
        actual_para_num_en =len(self.raw_text_en.split('\n'))
        tt = self.raw_text_zh.split('\n')[0]
        if actual_para_num_zh != self.zh_para_count:
            print(f"warning: {tt} zh para count error: calculated:{self.zh_para_count}; actual: {actual_para_num_zh}")
            self.zh_para_count = actual_para_num_zh
        if actual_para_num_en != self.en_para_count:
            print(f"warning: {tt} en para count error: calculated:{self.zh_para_count}; actual: {actual_para_num_en}")
            self.en_para_count = actual_para_num_en
        self.bi_para_ratio = self.get_ratio(self.zh_para_count, self.en_para_count)
        self.bi_sent_ratio = self.get_ratio(self.zh_sent_count, self.en_sent_count)
        self.bi_seg_ratio = self.get_ratio(self.zh_seg_count, self.en_seg_count)

    def clear_untr_marker(self,text, mark="r-z"):
        if mark == 'r-z':
            clean_text = re.sub(r"\s*\[PS\]\s*","\n", text)
            clean_text = re.sub(r"\|","", clean_text)
            clean_text = re.sub(r"\n\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]\s*\n","\n", clean_text)
            clean_text = re.sub(r"\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]\s*","", clean_text)
            clean_text = re.sub(r"\n\n+","\n", clean_text) 
        elif mark == 't-z':
            clean_text = re.sub(r"\s*\[PS\]/xm\s*","\n", text)
            clean_text = re.sub(r"\|/xn\s*","", clean_text)
            clean_text = re.sub(r"\n\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]/xw\s*\n","\n", clean_text)
            clean_text = re.sub(r"\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]/xw\s*"," ", clean_text)
            clean_text = re.sub(r"\n\n+","\n", clean_text) 
        elif mark == 'r-e':
            clean_text = re.sub(r"\s*\[PS\]\s*","\n", text)
            clean_text = re.sub(r"\|\s*","", clean_text)
            clean_text = re.sub(r"\n\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]\s*\n","\n", clean_text)
            clean_text = re.sub(r"\s*[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]\s*"," ", clean_text)
            clean_text = re.sub(r"\n\n+","\n", clean_text) 
        elif mark == 't-e':
            clean_text = re.sub(r"\s*\[PS\]_XM\s*","\n", text)
            clean_text = re.sub(r"\|_XN\s*","", clean_text)
            clean_text = re.sub(r"\n[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]_XW\s*\n","\n", clean_text)
            clean_text = re.sub(r"[\[〔]\s*(无|None|NONE|UnTr)\s*[\]〕]_XW\s*"," ", clean_text)
            clean_text = re.sub(r"\n\n+","\n", clean_text) 
        else:
            clean_text = text
        output_text =  re.sub(r"\n\n+","\n", clean_text)
        return output_text
    
    def generate_corpus(self, my_dict):
        self.get_info(my_dict)
        self.get_paras(my_dict)
        self.get_notes(my_dict)
        self.get_text()

    def get_word_tag_list(self):
        self.zh_byte_count, self.en_byte_count = self.dat.count_bytes(self.raw_text_zh, self.raw_text_en)
        self.zh_token_tag_list, self.zh_word_tag_list, self.zh_word_token_count, \
                                self.zh_word_type_count, self.zh_word_ttr, \
                                self.zh_word_sttr \
                                = self.dat.generate_word_tag_list(self.tag_text_zh, self.title_zh, "zh") 
        self.en_token_tag_list, self.en_word_tag_list, self.en_word_token_count = self.dat.generate_word_tag_list(self.tag_text_en, self.title_en, "en")

    def get_freq_dict(self):
        self.zh_token_tag_freq, self.zh_word_tag_freq, self.zh_token_output_dict, self.zh_word_output_dict \
                                = self.dat.count_freq(self.zh_token_tag_list, self.zh_word_tag_list, self.title_zh, "zh")
        self.en_token_tag_freq, self.en_word_tag_freq, self.en_word_tag_freq_list = self.dat.count_freq(self.en_token_tag_list, self.en_word_tag_list, self.title_en, "en")

    def get_output_dict(self):
        self.zh_token_output_dict = self.dat.initial_zlist_generator(self.zh_token_tag_freq, self.title_zh) 
        self.zh_word_output_dict = self.dat.initial_zlist_generator(self.zh_word_tag_freq, self.title_zh)
        self.en_token_output_dict = self.dat.initial_elist_generator(self.en_token_tag_freq, self.title_en)
        self.en_word_output_dict = self.dat.initial_elist_generator(self.en_word_tag_freq, self.title_en)

    def get_en_sttr(self):
        self.en_word_type_count, self.en_word_ttr, self.en_word_sttr = self.dat.count_en_sttr(self.en_word_token_count, self.en_word_output_dict, self.en_word_tag_freq_list)
        self.warnings.extend(self.dat.warning)
        
