#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Tony Chang (42716403@qq.com)

import pandas as pd

class SearchResultConverter:
    def __init__(self):
        pass

    def lst2pd(self, numlist, langlist, sentlist):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', 10000)
        df = pd.DataFrame({'num': numlist, \
                           'lang': langlist, \
                           'sent': sentlist})
        df.set_index(['num', 'lang'], inplace=True)
        return df    
    
    def pd2html(self,df_data):
        tm_html=df_data.to_html(header=None, index=True,index_names=False,escape=False,col_space='5',border='2')
        tm_html = tm_html.replace('border="2"',
                                  'border="2", style="border-collapse:collapse;"')
        tm_html = tm_html.replace('valign="top"',
                                  'valign="middle" align="center"')
        tm_html = tm_html.replace('<table',
                                  '<html>\n<body>\n<table cellpadding = "5"')
        tm_html = tm_html.replace('</table>',
                                  '</table>\n</body>\n</html>')
        tm_html = tm_html.replace('<th>',
                                  '<th valign="middle" align="center">')
        tm_html=tm_html.replace('font_color','font color')
        return tm_html

class VocFreqResultConverter:
    def __init__(self):
        pass

    def lst2pd(self, numlist, headlist, freqlist, lemmalist, lang="zh"):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', 10000)
        num = 'num'
        head = 'head'
        freq = 'freq'
        lemmas = "lemma & freq"
        if lang=="zh":
            num = '序号'
            head = '首词'
            freq = '总词频'
            lemmas = "词性及词频"
        df = pd.DataFrame({num: numlist, \
                           head: headlist, \
                           freq: freqlist,\
                           lemmas: lemmalist})
        df.set_index([num, head, freq, lemmas], inplace=True)
        return df    
    
    def pd2html(self,df_data):
        tm_html=df_data.to_html(header=None, index=True,index_names=True,escape=False,col_space='5',border='2')
        tm_html = tm_html.replace('border="2"',
                                  'border="2", style="border-collapse:collapse;"')
        tm_html = tm_html.replace('valign="top"',
                                  'valign="middle" align="center"')
        tm_html = tm_html.replace('<table',
                                  '<html>\n<body>\n<table cellpadding = "5"')
        tm_html = tm_html.replace('</table>',
                                  '</table>\n</body>\n</html>')
        tm_html = tm_html.replace('<th>',
                                  '<th valign="middle" align="center">')
        tm_html=tm_html.replace('font_color','font color')
        return tm_html    
