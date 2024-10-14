#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

from enum import Enum
import re

class SearchMode(Enum):
    NORMAL = 1
    EXTENDED = 2
    REGEX = 3

class SearchScope(Enum):
    ALL = 1
    SELECTED = 2
    CURRENT = 3
    GENRE = 4

class SearchRequest:
    def __init__(self):
        self.q = ''      
        self.dsp_nt = False
        self.dsp_sc = False
        self.dsp_ct = False
        self.mode: SearchMode = SearchMode.EXTENDED

class MatchResult:
    def __init__(self, start=0, end=0):
        self.start = start
        self.end = end

class SearchResultItem:
    def __init__(self):
        self.matches = []
        self.context_sl = []
        self.context_tl = []
        self.note_sl = []
        self.note_tl = []
        self.sent_num = ""
        self.sent_sl = ""
        self.sent_tl = ""
        self.art_id_sl = ""
        self.art_id_tl = ""
        self.art_title_sl = ""
        self.art_title_tl = ""
        self.sect_title_sl = ""
        self.sect_title_tl = ""
        self.sent_hi = ""

class SearchResult:
    def __init__(self):
        self.items = []
        self.num_list =[]
        self.lang_list = []
        self.sent_list =[]
        self.hit_words = 0
        self.hit_pairs = 0
