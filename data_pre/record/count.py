# -*- coding: utf-8 -*-
'''
Created on 2017��11��3��

@author: FeiFei
'''

from collections import defaultdict
from util.db import DB
from data_pre.record.match import extract_attr_value_jiancha
import codecs
import json
from util.string import parse_json



def count_jiancha():
    patterns=json.load(codecs.open("sources/patterns.json", 'r', encoding='utf-8'))
    conn=DB().connectSQL()
    cursor=conn.cursor()
    sql="select jiancha from bjoral_record"
    cursor.execute(sql)
    rows=cursor.fetchall()
    attr_val=defaultdict(list)
    for row in rows:
        result=extract_attr_value_jiancha(row,patterns["jiancha"],[])
        parse_json(result,attr_val)
    
    sorted_attr=sorted(attr_val.iteritems(),key=lambda asd:len(asd[1]),reverse=True)
    
    for i in range(10):
        print sorted_attr[i][0],len(sorted_attr[i][1])
    
    conn.commit()
    cursor.close()
    conn.close()

 
        
        
if __name__ == '__main__':
#     d1= {    "缺失": [
#       "缺失，"
#     ]}
#     d_all=defaultdict(list)
#     parse_json(d1,d_all)
#     for key,value in d_all.iteritems():
#         print key,value
    count_jiancha()