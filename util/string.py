# -*- coding: utf-8 -*-

'''
Created on 2017��10��11��

@author: FeiFei
'''

import re
import sys

reload(sys)
sys.setdefaultencoding('utf8') 

def rep_start_dup(s1):
    if re.search('\s+', s1)==None:
        return s1
    res=re.split('\s+', s1)
    f_res=res[1]
    tags=[r',',r'，',r';',r':',r'；',r'：',r'.']
    for tag in tags:
        if f_res.startswith(tag):
            if tag=='.':
                f_res=re.sub('\\'+tag, '', f_res, 1)
            else:
                f_res=re.sub(tag, '', f_res, 1)
    if f_res.startswith(res[0]):
        return re.sub(res[0]+'\s+', '', s1, 1)
    else:
        return s1

def parse_json(js,d_all):   
    if isinstance(js,dict):
        for key in js.keys():
            if isinstance(js.get(key),dict):
                parse_json(js.get(key),d_all)
            elif isinstance(js.get(key),list) and (isinstance(js.get(key)[0],str) or isinstance(js.get(key)[0],unicode)):
                d_all[key].extend(js.get(key))
            elif isinstance(js.get(key),list):
                parse_json(js.get(key),d_all)
            elif isinstance(js.get(key),str) or isinstance(js.get(key),unicode):
                d_all[key]=js.get(key)
                
    else:
        return   

if __name__ == '__main__':
    s1='缺失，剩余牙槽嵴中度吸收，近远中间隙基本正常，合龈间距基本正常。'
    print rep_start_dup(s1)