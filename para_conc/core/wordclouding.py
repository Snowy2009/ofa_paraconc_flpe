#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import re, copy, json
from collections import Counter, defaultdict
from amb_tank import AMB_TANK, AMB_LIST
from lemma_pos_map import LEMMA_POS_MAP, CAP_MAP, CHAR_FILTER

class Statistics:
    def __init__(self): 
        self.warning = []
        self.acronym_checklist = CAP_MAP["ACRONYM"]
        self.nnp_checklist = CAP_MAP["TITLE"]
        self.lower_checklist = CAP_MAP["SMALL"]
        self.char_strs = CHAR_FILTER        
        
    def count_bytes(self, text_zh, text_en):        
        return len(self.remove_added_marker(text_zh, "zh")),len(self.remove_added_marker(text_en, "en"))
          
    def remove_added_marker(self, text, lang = "zh"):
        if lang == "zh":
            text = re.sub(r"\ufeff","", text)
            text = re.sub(r"\|(/w|/xn) ", "", text) 
            text = re.sub(r"\[TI\]/xm ", "", text)
            text = re.sub(r"\[SU\]/xm ", "", text)
            text = re.sub(r"\[AU\]/xm ", "", text)         
            text = re.sub(r"\[DT\]/xm ", "", text) 
            text = re.sub(r"\[LO\]/xm ", "", text) 
            text = re.sub(r"\[(VL|ED)\]/xm ", "", text) 
            text = re.sub(r"\[CT\]/xm ", "", text) 
            text = re.sub(r"\[CH\]/xm ", "", text)
            text = re.sub(r"\[SC\]/xm ", "", text)
            text = re.sub(r"\[PU\]/xm ", "", text) 
            text = re.sub(r"\[NT\]/xm ", "", text) 
            text = re.sub(r"\[AX\]/xm ", "", text) 
            text = re.sub(r"\[P.*?\]/xm ", "", text) 
            #text = re.sub(r"〔/wkz [a-z]/\w+ 〕/wky", "*/w", text) 
            text = re.sub(r"〔/wkz (无/\w+|照片/\w+) 〕/wky\n*","", text) 
            text = re.sub(r"〔(无/\w+|照片/\w+)〕/xw\n*","", text) 
        if lang == "en":
            text = re.sub(r"\ufeff","", text)
            text = re.sub(r"\|_XN ", "", text) 
            text = re.sub(r"\[TI\]_XM ", "", text)
            text = re.sub(r"\[SU\]_XM ", "", text)
            text = re.sub(r"\[CT\]_XM ", "", text)
            text = re.sub(r"\[AU\]_XM ", "", text)
            text = re.sub(r"\[DT\]_XM ", "", text)
            text = re.sub(r"\[LO\]_XM ", "", text)
            text = re.sub(r"\[SC\]_XM ", "", text)
            text = re.sub(r"\[PU\]_XM ", "", text)
            text = re.sub(r"\[(VL|ED)\]_XM ", "", text)  
            text = re.sub(r"\[AX\]_XM ", "", text)
            text = re.sub(r"\[NT\]_XM ", "", text)
            text = re.sub(r"\[CH\]_XM ", "", text)
            text = re.sub(r"\[P.*?\]_XM ", "", text) 
            text = re.sub(r"\[_\[ P.*?\]_\] ", "", text)      
            text = re.sub(r"\[_\[ (UnTr_\w+|PHOTOS_\w+) ]_]\n*","", text) 
            text = re.sub(r"\[(UnTr_\w+|PHOTOS_\w+)]_XW\n*","", text) 
        return text

    def generate_word_tag_list(self, tagged_text, file_id, lang = "zh"):        
        clean_text = self.remove_added_marker(tagged_text, lang) 
        char_regex = r'[一二三四五六七八九十百千万亿兆]'
        token_tag_list = []
        word_tag_list = []
        if lang == "zh":          
            para_list = [x.strip() for x in clean_text.split("\n") if x.strip()]
            for para in para_list:                
                word_tags = [y for y in para.split()]
                for word_tag in word_tags:
                    if word_tag.startswith("//"):  
                        token_tag_list.append(('/',word_tag.split("/")[-1])) 
                    elif word_tag.startswith("/"):  
                        token_tag_list.append(('[空格]',"None")) 
                    elif "/" in word_tag:        
                        words = [x for x in word_tag.split("/") if x.strip()]
                        if len(words) == 1:      
                            msg = f"ZH WdTgSplit ERROR in {file_id}: {word_tag}"
                            if msg not in self.warning:
                                self.warning.append(msg)
                        else: 
                            if len(words)==2:
                                w = words[0]  
                                t = words[1] 
                            else:            
                                w = "/".join(words[:-1])  
                                t = words[-1]             
                            if t.startswith('w'):
                                token_tag_list.append((w, t)) 
                            elif t.startswith("xu"):
                                token_tag_list.append((w, t)) 
                            elif t in ["xm", 'xn', "xw"]:
                                pass 
                            elif w in '&‘’“”（）—；。，%‰□■$#"*+-@•…':
                                token_tag_list.append((w,t)) 
                            elif t == "m":
                                char_test = re.search(char_regex, w)
                                if char_test:
                                    token_tag_list.append((w, t)) 
                                    word_tag_list.append((w, t)) 
                                else:
                                    token_tag_list.append((w, t))
                            else:
                                token_tag_list.append((w, t))
                                word_tag_list.append((w, t))
                    else: 
                        msg = f"ZH TagMissing ERROR in {file_id}: {word_tag}"
                        if msg not in self.warning:
                            self.warning.append(msg)
            if token_tag_list and word_tag_list:
                token_count, word_type_count, word_ttr, word_sttr = self.count_zh_sttr(word_tag_list)
                return token_tag_list, word_tag_list, token_count, word_type_count, word_ttr, word_sttr
            else:
                return "", "", "", "", "", ""
        if lang == "en":            
            para_list = [x.strip() for x in clean_text.split("\n") if x.strip()]
            for para in para_list:
                word_tags = [y for y in para.split()]
                for word_tag in word_tags:
                    if word_tag.startswith("_"):
                        token_tag_list.append(('[空格]',word_tag.replace("_",""))) 
                    elif "_" in word_tag: 
                        words = [x for x in word_tag.split("_") if x.strip()]
                        if len(words) > 1:
                            w = words[0]
                            t = words[1]
                            if t == "None":
                                token_tag_list.append((w,t))
                            elif t[0] in '[]:?;,.`/()':
                                token_tag_list.append((w,t))
                            elif w.isnumeric():
                                token_tag_list.append((w,t)) 
                            elif t == "SYM":
                                token_tag_list.append((w,t)) 
                            elif w in '=&‘’“”（）—；。，%‰□■$#"*+-@•…':
                                token_tag_list.append((w,t)) 
                            else:
                                token_tag_list.append((w, t))
                                word_tag_list.append((w, t))
                        else:
                            if word_tag.lstrip().rstrip().startswith("_"):
                                token_tag_list.append(('[空格]',word_tag.replace("_","").strip())) 
                            else:
                                msg = f"EN TAG ERROR in {file_id}: {word_tag} Detailed info: tg is missing"
                                if msg not in self.warning:
                                    self.warning.append(msg) 
                    else:
                        msg = f"EN NoTag Marker ERROR in {file_id}: {word_tag} Detailed info: no _ found!"
                        if msg not in self.warning:
                            self.warning.append(msg) 
            if token_tag_list and word_tag_list:
                word_token_count = len(word_tag_list)
                return token_tag_list, word_tag_list, word_token_count 
 
    def count_zh_sttr (self, token_list):
        token_count = len(token_list)
        type_count = len(set([word for (word, tag) in token_list]))    
        try:
            ttr = type_count/token_count
        except:
            self.warning.append("critical zero error occurred!")
        if len(token_list) < 1000:
            sttr = 0
        else:
            start = 0
            interval = 1000
            ttrs = []
            while start <= len(token_list) - interval:
                section = token_list[start:start + interval]
                tk_count = len(section)
                ty_count = len(set([word for (word, tag) in section]))
                section_ttr = ty_count / tk_count
                ttrs.append(section_ttr)
                start += interval
            if ttrs:
                sttr = sum(ttrs)/len(ttrs)
            else:
                self.warning.append("STTR generating error occurred!")
                sttr = 0
        return token_count, type_count, ttr, sttr
    
    def count_en_sttr(self, word_token_count, output_dict, sep_wtf_list):
        word_type_count = len(output_dict.keys())
        en_word_ttr = word_type_count/word_token_count
        if not sep_wtf_list:            
            en_word_sttr = 0
        else:
            tt = 0
            tn = len(sep_wtf_list)
            for wtf_dict in sep_wtf_list:
                t_dict = self.initial_elist_generator(wtf_dict)
                t_type = len(t_dict.keys())
                t_token = 1000
                tt += t_type/t_token
            en_word_sttr = tt/tn
        return word_type_count, en_word_ttr, en_word_sttr
       
    def count_freq(self, token_tag_list, word_tag_list, text_title, lang="zh"):
        target_length = len(word_tag_list)
        token_tag_freq = {}
        word_tag_freq = {}
        word_tag_freq_list=[]
        token_output_dict={}
        word_output_dict={}
        if lang == "zh":            
            try:
                token_tag_freq = Counter((word, tag) for (word, tag) in token_tag_list)
            except:
                self.warning.append(f"critical zh token tag freq counting error occurred in {text_title}!")
            try:
                word_tag_freq = Counter((word, tag) for (word, tag) in word_tag_list)
            except:
                self.warning.append(f"critical zh word tag freq counting error occurred in {text_title}!")
            if token_tag_freq:
                token_output_dict = self.initial_zlist_generator(token_tag_freq)
            if word_tag_freq:
                word_output_dict = self.initial_zlist_generator(word_tag_freq)
            return token_tag_freq, word_tag_freq, token_output_dict, word_output_dict 
        if lang == "en":
            try:
                token_tag_freq = Counter((word , tag) for (word, tag) in token_tag_list)
            except:
                self.warning.append(f"critical en token tag freq counting error occurred in {text_title}!")
            try:
                word_tag_freq = Counter((word , tag) for (word, tag) in word_tag_list)
            except:
                self.warning.append(f"critical en word tag freq counting error occurred in {text_title}!")
            if target_length >= 1000:
                wt_freq = {}
                start = 0
                interval = 1000
                while start <= len(word_tag_list) - interval:
                    sect_list = word_tag_list[start:start + interval]
                    try:
                        wt_freq = Counter((word, tag) for (word, tag) in sect_list)
                        word_tag_freq_list.append(wt_freq)
                    except:
                        self.warning.append(f"critical en word tag sttr freq counting error occurred in {text_title}!")
                    start += interval
            return token_tag_freq, word_tag_freq, word_tag_freq_list
        
    def zh_word_merger(self, temp_wd):
        final_dict = {}
        merge_dict = defaultdict(list)        
        for key, item_list in temp_wd.items():
            temp_dict = {}
            for (w, t, q) in item_list:
                if (w,t) not in temp_dict.keys():
                    temp_dict[(w,t)] = q
                else:
                    temp_dict[(w,t)] += q
            for (w,t), q in temp_dict.items():
                merge_dict[key].append((w,t,q))
        for key, item_list in merge_dict.items():
            t_q = 0
            for (w, t, q) in item_list:
                t_q += q
            final_dict[(key, t_q)]=item_list
        return final_dict
    
    def en_pos_filter(self, word, tag):
        if word in ["-","'","/","+", "=", "&", "$", "[", "]"]:
            pass
        elif "-" in word:
            ws = word.split("-")[0]
            if tag in ["CC", "DT", "EX","MD", "JJS", "JJR", "UH", "PDT", "POS", "PRP$", \
                   "RP", "RB", "RBR", "RBS","TO", "IN", "WDT", "WP", "WP$", \
                   "WRB", "SYM", ".", ",", ":", "(", ")", "$", "``", "''"]:
                word = word.lower()
            elif tag in ["PRP"]:
                word = word.lower()
            elif ws in self.nnp_checklist or ws in self.acronym_checklist or ws == "I":
                pass
            elif ws.lower() in self.lower_checklist:
                word = word.lower()
            elif tag.startswith("V") and ws not in self.nnp_checklist and ws not in self.acronym_checklist:
                word = word.lower()
            else:
                pass
        elif "'" in word:
            ws = word.split("'")[0]
            if tag in ["CC", "DT", "EX","MD", "JJS", "JJR", "UH", "PDT", "POS", "PRP$", \
                   "RP", "RB", "RBR", "RBS","TO", "IN", "WDT", "WP", "WP$", \
                   "WRB", "SYM", ".", ",", ":", "(", ")", "$", "``", "''"]:
                word = word.lower()
            elif tag in ["PRP"]:
                word = word.lower()
            elif ws in self.nnp_checklist or ws in self.acronym_checklist or ws == "I":
                pass
            elif ws.lower() in self.lower_checklist:
                word = word.lower()
            elif tag.startswith("V") and ws not in self.nnp_checklist and ws not in self.acronym_checklist:
                word = word.lower()
            else:
                pass
        elif "/" in word:
            ws = word.split("/")[0]
            if tag in ["CC", "DT", "EX","MD", "JJS", "JJR", "UH", "PDT", "POS", "PRP$", \
                   "RP", "RB", "RBR", "RBS","TO", "IN", "WDT", "WP", "WP$", \
                   "WRB", "SYM", ".", ",", ":", "(", ")", "$", "``", "''"]:
                word = word.lower()
            elif tag in ["PRP"]:
                word = word.lower()
            elif ws in self.nnp_checklist or ws in self.acronym_checklist or ws == "I":
                pass
            elif ws.lower() in self.lower_checklist:
                word = word.lower()
            elif tag.startswith("V") and ws not in self.nnp_checklist and ws not in self.acronym_checklist:
                word = word.lower()
            else:
                pass 
        elif "+" in word:
            ws = word.split("+")[0]
            if tag in ["CC", "DT", "EX","MD", "JJS", "JJR", "UH", "PDT", "POS", "PRP$", \
                   "RP", "RB", "RBR", "RBS","TO", "IN", "WDT", "WP", "WP$", \
                   "WRB", "SYM", ".", ",", ":", "(", ")", "$", "``", "''"]:
                word = word.lower()
            elif tag in ["PRP"]:
                word = word.lower()
            elif ws in self.nnp_checklist or ws in self.acronym_checklist or ws == "I":
                pass
            elif ws.lower() in self.lower_checklist:
                word = word.lower()
            elif tag.startswith("V") and ws not in self.nnp_checklist and ws not in self.acronym_checklist:
                word = word.lower()
            else:
                pass 
        elif "[" in word:
            word= word.replace("[","").replace("]","")
            if tag in ["CC", "DT", "EX","MD", "JJS", "JJR", "UH", "PDT", "POS", "PRP$", \
                   "RP", "RB", "RBR", "RBS","TO", "IN", "WDT", "WP", "WP$", \
                   "WRB", "SYM", ".", ",", ":", "(", ")", "$", "``", "''"]:
                word = word.lower()
            elif tag in ["PRP"]:
                word = word.lower()
            elif word in self.nnp_checklist or word in self.acronym_checklist or word == "I":
                pass
            elif word.lower() in self.lower_checklist:
                word = word.lower()
            elif tag.startswith("V") and word not in self.nnp_checklist and word not in self.acronym_checklist:
                word = word.lower()
            else:
                pass 
        else:
            if tag in ["CC", "DT", "EX","MD", "FW", "JJS", "JJR", "UH", "PDT", "POS", "PRP$", \
                   "RP", "RB", "RBR", "RBS","TO", "IN", "WDT", "WP", "WP$", \
                   "WRB", "SYM", ".", ",", ":", "(", ")", "$", "``", "''"]:
                word = word.lower()
            elif tag in ["PRP"] and word != "I":
                word = word.lower()
            elif word in self.nnp_checklist or word in self.acronym_checklist or word == "I":
                pass
            elif word.lower() in self.lower_checklist:
                word = word.lower()
            elif tag.startswith("V") and word not in self.nnp_checklist and word not in self.acronym_checklist:
                word = word.lower()
            else:
                pass
        return word, tag
        
    def check_lemma(self, src_word, src_tag):
        head_word = ""
        family_index = 0
        if src_word in AMB_LIST:
            head_word = self.check_amb(src_word, src_tag)
            family_index += 1
        elif src_word in LEMMA_POS_MAP.keys():
            head_word == src_word
            family_index += 1
        if family_index == 0:
            head_index = 0
            for head in LEMMA_POS_MAP.keys():
                for head_tag in LEMMA_POS_MAP[head].keys():
                    if src_word in LEMMA_POS_MAP[head][head_tag]:
                        try:
                            head_word = head
                            head_index += 1
                        except:
                            pass
        return head_word 
        
    def check_amb(self, src_wrd, src_tag):
        amb_word = ""
        src_l = src_wrd
        if src_wrd != src_wrd.lower():
            src_l = src_wrd.lower()
        i = 0
        for amb_head, amb_list in AMB_TANK.items():
            for item in amb_list:
                for lm, tg in item.items():
                    if src_l == lm and src_tag == tg:
                        amb_word = amb_head
                        i += 1                                    
        if i == 0:
            for amb_head, amb_list in AMB_TANK.items():
                if src_l == amb_head:
                     amb_word = amb_head
                     i += 1                                        
        return amb_word

    def word_merger(self, temp_wd, pid = ""):
        lemma_dict =defaultdict(list)
        final_dict = {}
        merge_dict = defaultdict(list)        
        for key, item_list in temp_wd.items():
            temp_dict = {}
            for (w, t, q) in item_list:
                if (w,t) not in temp_dict.keys():
                    temp_dict[(w,t)] = q
                else:
                    temp_dict[(w,t)] += q
            for (w,t), q in temp_dict.items():
                merge_dict[key].append((w,t,q))
        for key, item_list in merge_dict.items():
            t_q = 0
            for (w, t, q) in item_list:
                t_q += q
            final_dict[(key, t_q)]=item_list
        return final_dict
    
    def dict_merger(self, temp_wd, pid = ""):
        merge_dict={}
        temp_dict = defaultdict(list)
        for key, itm_list in temp_wd.items():
            for (t, q) in itm_list:
                temp_dict[key].append((key, t, q))
        for key, item_list in temp_dict.items():            
            t_q = 0
            for (w, t, q) in item_list:
                t_q += q
            merge_dict[(key, t_q)]=item_list
        final_dict = defaultdict(list)
        for k in merge_dict.keys():
            il = len(merge_dict[k])
            if il == 1:
                final_dict[k]=copy.deepcopy(merge_dict[k])
            else:
                re_dict = {}
                for (w, t, f) in merge_dict[k]:
                    #if t != "NNP":
                    #    w = w.lower()
                    if (w,t) not in re_dict.keys():
                        re_dict[(w,t)]= f
                    else:
                        re_dict[(w,t)]+=f
                for (w,t), f in re_dict.items():
                    final_dict[k].append((w,t,f))            
                
        return final_dict
        
    def initial_zlist_generator(self, raw_token_tag_freq, file_id = ""): 
        num_regex = r'\d'
        word_wd = defaultdict(list) 
        for (w,t), f in raw_token_tag_freq.items():
            r = re.search(num_regex, w)
            if t.startswith("w"):
                word_wd[w].append((w, t, f))
            elif t=="None":
                word_wd[w].append((w, t, f))
            elif w[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                word_wd[w].append((w, t, f))  
            elif r:
                word_wd[w].append((w, t, f))  
            elif t.startswith("m"):
                word_wd[w].append((w,t, f))
            elif w.isalnum():
                word_wd[w].append((w, t, f))                
            elif "•" in w and t in ["nz", "nr", "nrf"]: 
                word_wd[w].append((w, t, f))
            elif "·" in w and t in ["nz", "nr", "nrf"]:
                word_wd[w].append((w, t, f))
            elif "/" in  w:
                word_wd[w].append((w, t, f))
            else:
                if file_id:
                    msg = f"WARNING: unknown zh words found in {file_id}: {w}/{t}/{f}"
                else:
                    msg = f"WARNING: unknown zh words found in: {w}/{t}/{f}"
                if msg not in self.warning:
                    self.warning.append(msg)                
        n_word_wd = self.zh_word_merger(word_wd)
        zh_output_dict = n_word_wd
        return zh_output_dict

    def cap_low_checher(self, w, t):        
        if w.islower():
            nature = "low"
        elif w.isupper() or w.istitle():
            if w in self.acronym_checklist or w in self.nnp_checklist:
                nature = "cap"
            elif "NNP" in t:
                if w.lower() in self.lower_checklist:
                    nature = "cap-low"
                else:
                    nature = "cap"
            else:
                nature = "cap-unknown"
        else:
            nature = "unknown"
        return nature

    def initial_elist_generator(self, raw_token_tag_freq, file_id = ""):
        word_wd = defaultdict(list) 
        num_regex = r'\d'
        for (w,t), f in raw_token_tag_freq.items():
            wd,tg = self.en_pos_filter(w, t) 
            r = re.search(num_regex, w)
            if t in ["XM", "XN", "XW"]:                         
                pass
            elif not t.isalpha() and not t.endswith('P$') or t == "SYM" : 
                try:                       
                    word_wd[wd].append((w, t, f))
                except:
                    print(w,t,f)
            elif t == "FW":
                word_wd[wd].append((w,t,f)) # 外来语 -> foreign_wd                     
            elif r:
                if '-' in w:
                    word_wd[wd].append((w, t, f))
                elif t.startswith("NNP"):
                    word_wd[w].append((w, t, f))
                else:
                    word_wd[wd].append((w, t, f))    
            elif t == "CD" or t == "LS":
                if w.isupper():
                    word_wd[w].append((w, t, f))            
                else:
                    word_wd[wd].append((w, t, f))
            elif len(w)>2 and "-" in w:                  
                word_wd[wd].append((w, t, f))       
            elif len(w)>1 and w.isupper() or "." in w:
                if w not in ['FOREIGN', 'LANGUAGE', 'TEACHING',\
                             'AND', 'RESEARCH', 'PRESS', 'HIGHER',\
                             'EDUCATION'] and "." not in w:
                    word_wd[w].append((w, t, f))
                else:
                    lem = self.check_lemma(wd, t)
                    if lem:
                        word_wd[lem].append((w, t, f))
                    else:
                        word_wd[wd].append((w, t, f))
            elif w.isalnum() or t == "PRP$":                
                lem = self.check_lemma(wd, t)
                if lem:
                    word_wd[lem].append((w, t, f))
                else:
                    word_wd[wd].append((w, t, f)) 
            elif "[" in w:
                lem = self.check_lemma(wd, t)
                if lem:
                    word_wd[lem].append((w, t, f))
                else:
                    word_wd[wd].append((w, t, f))
            elif "'" in w:               
                lem = self.check_lemma(w, t)
                if lem:
                    word_wd[lem].append((w, t, f))
                else:
                    word_wd[wd].append((w, t, f))
            elif w == "/":
                word_wd[wd].append((w, t, f))
                if t not in ["CC", "IN"]:
                    if file_id:
                        msg = f"wrong_en_tag found in {file_id}: {w}, {t}, {f}"
                    else:
                        msg = f"wrong_en_tag found: {w}, {t}, {f}"
                    if msg not in self.warning:
                        self.warning.append(msg)
            elif w == '&':
                word_wd[w].append((w, t, f))
                if t != "CC":
                    if file_id:
                        msg = f"wrong_en_tag found in {file_id}: {w}, {t}, {f}"
                    else:
                        msg = f"wrong_en_tag found: {w}, {t}, {f}"
                    if msg not in self.warning:
                        self.warning.append(msg)
            elif w == '%':
                word_wd[w].append((w, t, f))
                if t != "NN":
                    if file_id:
                        msg = f"wrong_en_tag found in {file_id}: {w}, {t}, {f}"
                    else:
                        msg = f"wrong_en_tag found: {w}, {t}, {f}"
                    if msg not in self.warning:
                        self.warning.append(msg)
            elif w == '+':
                word_wd[w].append((w, t, f))
                if t != "CC":
                    if file_id:
                        msg = f"wrong_en_tag found in {file_id}: {w}, {t}, {f}"
                    else:
                        msg = f"wrong_en_tag found: {w}, {t}, {f}"
                    if msg not in self.warning:
                        self.warning.append(msg)
            elif w == "=": # 单词为+或=
                word_wd[w].append((w, t, f))
                if t != "VBZ":
                    if file_id:
                        msg = f"wrong_en_tag found in {file_id}: {w}, {t}, {f}"
                    else:
                        msg = f"wrong_en_tag found: {w}, {t}, {f}"
                    if msg not in self.warning:
                        self.warning.append(msg)
            elif "+" in w: # 单词内包含+                
                if "NN" in t:
                    word_wd[wd].append((w, t, f))
                else:
                    if file_id:
                        msg = f"wrong_en_tag found in {file_id}: {w}, {t}, {f}"
                    else:
                        msg = f"wrong_en_tag found: {w}, {t}, {f}"
                    if msg not in self.warning:
                        self.warning.append(msg)                    
            else:
                if file_id:
                    msg = f"unkn_en_wd found in {file_id}: {w}, {t}, {f}"
                else:
                    msg = f"unkn_en_wd found: {w}, {t}, {f}"
                if msg not in self.warning:
                    self.warning.append(msg)      
        n_word_wd = self.word_merger(word_wd, "TITLE")
        en_output_dict = n_word_wd
        return en_output_dict
