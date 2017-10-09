# -*- coding: utf-8 -*-
'''
Created on 2017��10��1��

@author: FeiFei
'''
import re
import chardet

if __name__ == '__main__':
    pattern='X线片示(.*?)[\r\n]'
    s1='''X线片示：冠部充填物高密度影达髓腔,冠部近中可见裂纹影像，根管内 充填物影像，根尖周无低密度影。
'''
#     print pattern,chardet.detect(pattern)
#     print s1,chardet.detect(s1)
#     print s1.replace("要求", "，要求")
    print 's1',re.findall(pattern,s1)
    print 's1[0]',re.findall(pattern,s1)[0]
    print 's1[0][1]',re.findall(pattern,s1)[0][1]