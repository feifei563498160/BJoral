# -*- coding: utf-8 -*-
'''
Created on 2017��10��1��

@author: FeiFei
'''
import re
import chardet

if __name__ == '__main__':
    pattern='((([ⅠⅡⅢ]|I+)[度°]*[-~]([ⅠⅡⅢ]|I+)[度°]*)|([ⅠⅡⅢ]|I+|[123一二三])[+-]*[°度]*[+-]*[,；]*|[不无])松动'
    s1='''松动
'''
#     print pattern,chardet.detect(pattern)
#     print s1,chardet.detect(s1)
#     print s1.replace("要求", "，要求")
    print 's1',re.findall(pattern,s1)
    print 's1[0]',re.findall(pattern,s1)[0]
    print 's1[0][0]',re.findall(pattern,s1)[0][0]