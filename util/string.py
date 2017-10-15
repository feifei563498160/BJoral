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
    
if __name__ == '__main__':
    s1='牙体治疗     牙体治疗    这就是'
    print rep_start_dup(s1)