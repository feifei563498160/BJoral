# -*- coding: utf-8 -*-
'''
Created on 2017��10��9��

@author: FeiFei
'''
import codecs
from collections import Counter
import chardet
import sys

reload(sys)
sys.setdefaultencoding('utf8') 

def list2set(inpath,outpath):
    wf=codecs.open(outpath, 'w', 'utf-8')
    for item in sorted(Counter(codecs.open(inpath, 'r', 'utf-8').readlines()).iteritems(),key=lambda asd:asd[1],reverse=True):
        wf.write(item[0].encode('utf-8').strip()+' : '+str(item[1])+'\n')



if __name__ == '__main__':
    
    list2set('list.txt','set.txt')