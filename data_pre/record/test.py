# -*- coding: utf-8 -*-
'''
Created on 2017��10��1��

@author: FeiFei
'''
import re
import json
import chardet
import codecs

from collections import defaultdict

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
def get_beizhu(s1):
    beizhu=[]
    if u'?' in s1: 
        beizhu.append(u'?')
    if u'？' in s1:
        beizhu.append(u'？')
    result=re.findall(u"([(（]+(.*?)[)）]+)", s1)
    if len(result)!=0:
        for ele in result:
            beizhu.append(ele[1])
    return beizhu,re.sub(u"([(（]+(.*?)[)）]+)|[?？]", u"", s1)

def test_match():
    #(，|。|；|,|;|\r|\n)
    #卫生状况[：]*(.*?)[，。；,;\r\n]
    #?P<content>
    pattern=u"[\\d]*\\.(?P<content>.*)"
    s1=u'''\n    1.不拔牙矫治（必要时小量邻面去釉）'''
#     print re.split(pattern, s1)
#     p=re.compile(pattern)
#     print p.groupindex
#     print pattern,chardet.detect(pattern)
#     print s1,chardet.detect(s1)
#     print s1.replace("要求", "，要求")
#     m=re.search(pattern, s1)
#     print len(m.groupdict())
#     print m.groupdict()
#     s3=m.groupdict()['content1']
#     print s3
    print 's1',re.findall(pattern,s1)
    print 's1[0]',re.findall(pattern,s1)[0]
    print 's1[0][0]',re.findall(pattern,s1)[2][2]

def test_json():
    attr2value=defaultdict(list)
    mczcjc_dict=defaultdict(list)
    mczcjc_dict["检查位置"].append('mjcwz')
    mczcjc_dict["牙冠外形"].append('mygwx')
    attr2value["萌出智齿检查"].append(mczcjc_dict)
    print attr2value
    json.dump(attr2value, codecs.open("test_json.json", 'w','utf-8'),ensure_ascii=False,indent=2)
    
    
if __name__ == '__main__':
#     print get_beizhu(u"外院牙髓治疗后(残冠)(banyin)?？")
    test_match()
#     test_json()