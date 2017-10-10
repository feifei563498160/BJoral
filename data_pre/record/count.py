# -*- coding: utf-8 -*-
'''
Created on 2017年9月20日

@author: FeiFei
'''
import os
import xlrd
import re
import jieba

from util.mylogger import log_file
from collections import Counter

import sys
import codecs
import chardet
import traceback
import jieba.posseg as postag

reload(sys)
sys.setdefaultencoding('utf8') 


logger_split_freq=log_file('log/log_split_freq.log','split_freq_log')
logger_concept=log_file('log/log_concepts.log','concepts_log')
logger_test=log_file('log/test.log','test_log')
logger_word_freq=log_file('log/log_word_freq.log','word_freq_log')
logger_exp=log_file('log/log_exp.log','exp_log')
logger_filter_oral=log_file('log/log_filter_oral.log','filter_oral_log')
logger_oral_word=log_file('log/log_oral_word.log','oral_word_log')

logger_zhusu=log_file("seg/log_zhusu", "zhusu_log")
logger_xianbingshi=log_file("seg/log_xianbingshi", "xianbingshi_log")
logger_jiwangshi=log_file("seg/log_jiwangshi", "jiwangshi_log")
logger_jiazushi=log_file("seg/log_jiazushi", "jiazushi_log")
logger_quanshen=log_file("seg/log_quanshen", "quanshen_log")
logger_jiancha=log_file("seg/log_jiancha", "jiancha_log")
logger_zhenduan=log_file("seg/log_zhenduan", "zhenduan_log")
logger_zhiliaojihua=log_file("seg/log_zhiliaojihua", "zhiliaojihua_log")
logger_chuzhi=log_file("seg/log_chuzhi", "chuzhi_log")

logger_test=log_file("seg/log_test", "test_log")

logger_attr=log_file("log/attr_test", "attr_log")

def filter_concept(concept):
    c1=len(concept)<7
    c=False
    words=['的']
    for word in words:
        c=c or (word in  concept and concept.index(word)!=len(concept)-1)
    c2='的' in  concept and concept.index('的')!=len(concept)-1
    c3='及' in  concept and concept.index('及')!=len(concept)-1
    c3='及' in  concept and concept.index('及')!=len(concept)-1
    c4=concept.startswith('的') or concept.startswith('及') 
#     if c1 and ((c2 and c1) or (c3 and c1)):
#         return True
    if c:
        return True
def medical_concept(inpath):
    lines=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            file=codecs.open(new_path,'r','utf-8')
            lines.extend(file.readlines())
    cnt_ecp=0
    cnt_long=0
    for line in set(lines):
        if filter_concept(line.strip().decode('utf-8')):
            print line.strip().decode('utf-8')
#         str_tmp=line.strip().decode('utf-8')
#             cnt_long+=1
#             print str_tmp

#         if len(line)>10:
#             try:
#                 cnt_long+=1
#                 print line.strip().decode('utf-8')
#             except Exception:
#                 cnt_ecp+=1
#                 traceback.print_exc(Exception)
#                 logger_concept.info(line.strip()+": except")

#         logger_concept.info(line.strip().decode('utf-8'))
#     print cnt_ecp,cnt_long,len(set(lines))
    return lines    

def filter_record(record):
    if '诊断：' not in record or ('处 置：' not in record and '处置：' not in record) or ('治疗计划：' not in record and '治疗设计：' not in record):
        return False
    return True
   

def is_oral_concept(concept):
    signs=['牙','口','齿','颌','冠','龈','腭','舌','腮','根','龋','唇','乳头']
    for sign in signs:
        if sign in concept:
            return True
    return False

def filter_oral_concepts():
    inpath='concepts_all/filter'
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            file=codecs.open(new_path, 'r', encoding='utf-8')
            for line in file.readlines():
                if is_oral_concept(line.strip()):
                    logger_filter_oral.info(line.strip())
            

def merge_concept():
    inpath='concepts'
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            file=codecs.open(new_path, 'r', encoding='utf-8')
            for line in file.readlines():
#                 if is_oral_concept(line.strip()):
                    logger_oral_word.info(line.strip())
                    
                        
def analysis_record(record):
    zhusu=re.findall(r'主  诉：([\s\S]*)现病史：',record)[0].strip()
    xianbingshi=re.findall(r'现病史：([\s\S]*)既往史：',record)[0].strip()
    jiwangshi=re.findall(r'既往史：([\s\S]*)家族史：',record)[0].strip()
    jiazushi=re.findall(r'家族史：([\s\S]*)全  身：',record)[0].strip()
    quanshen=re.findall(r'全  身：([\s\S]*)检  查：',record)[0].strip()
    jiancha=re.findall(r'检  查：([\s\S]*)诊断：',record)[0].strip()
    zhenduan=re.findall(r'诊断：([\s\S]*)治疗计划：',record)[0].strip()
    zhiliaojihua=re.findall(r'治疗计划：([\s\S]*)处 置：',record)[0].strip()
    chuzhi=re.findall(r'处 置：([\s\S]*)签名',record)[0].strip()
    
#     jieba.load_userdict("sources/concepts_dict.txt")
    jieba.load_userdict("sources/user_dict.txt")
    
    zhusu_seg_list = jieba.cut(zhusu)
    xianbingshi_seg_list = jieba.cut(xianbingshi)
    jiwangshi_seg_list = jieba.cut(jiwangshi)
#     if "否认" in jiazushi:
#         print jiazushi
    jiazushi_seg_list = jieba.cut(jiazushi)
    quanshen_seg_list = jieba.cut(quanshen)
    jiancha_seg_list = jieba.cut(jiancha)
    zhenduan_seg_list = jieba.cut(zhenduan)
    zhiliaojihua_seg_list = jieba.cut(zhiliaojihua)
    chuzhi_seg_list = jieba.cut(chuzhi)
    return zhusu_seg_list,xianbingshi_seg_list,jiwangshi_seg_list,jiazushi_seg_list, \
        quanshen_seg_list,jiancha_seg_list,zhenduan_seg_list,zhiliaojihua_seg_list,chuzhi_seg_list


def count_record():
    inpath='records'
    zhusu_seg_list=[]
    xianbingshi_seg_list=[]
    jiwangshi_seg_list=[]
    jiazushi_seg_list=[]
    quanshen_seg_list=[]
    jiancha_seg_list=[]
    zhenduan_seg_list=[]
    zhiliaojihua_seg_list=[]
    chuzhi_seg_list=[]
    cnt_r=0
    for rt, dirs, files in os.walk(inpath):
            for f in files:
                fname = os.path.splitext(f)
                new_path = inpath+os.sep+fname[0] + fname[1]
                data=xlrd.open_workbook(new_path)
                table=data.sheets()[0]
                nrows = table.nrows
                for i in range(2,nrows):
                    sex=table.cell(i,1).value
                    record=table.cell(i,5).value
#                     print record
#                     print new_path.decode('gbk')
#                     if filter_record(record)==False:
#                         continue
#                     print cnt_r
                    try:
                        zhusu_seg,xianbingshi_seg,jiwangshi_seg,jiazushi_seg, \
                        quanshen_seg,jiancha_seg,zhenduan_seg,zhiliaojihua_seg,chuzhi_seg=analysis_record(record.encode('utf-8'))
                        zhusu_seg_list.extend(zhusu_seg)
                        xianbingshi_seg_list.extend(xianbingshi_seg)
                        jiwangshi_seg_list.extend(jiwangshi_seg)
                        jiazushi_seg_list.extend(jiazushi_seg)
                        quanshen_seg_list.extend(quanshen_seg)
                        jiancha_seg_list.extend(jiancha_seg)
                        zhenduan_seg_list.extend(zhenduan_seg)
                        zhiliaojihua_seg_list.extend(zhiliaojihua_seg)
                        chuzhi_seg_list.extend(chuzhi_seg)
                        cnt_r+=1
                    except Exception:
                        logger_exp.info(record)
                        logger_exp.info(traceback.format_exc())


    c_zhusu_seg_list=sorted(Counter(zhusu_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_xianbingshi_seg_list=sorted(Counter(xianbingshi_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_jiwangshi_seg_list=sorted(Counter(jiwangshi_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_jiazushi_seg_list=sorted(Counter(jiazushi_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_quanshen_seg_list=sorted(Counter(quanshen_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_jiancha_seg_list=sorted(Counter(jiancha_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_zhenduan_seg_list=sorted(Counter(zhenduan_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_zhiliaojihua_seg_list=sorted(Counter(zhiliaojihua_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    c_chuzhi_seg_list=sorted(Counter(chuzhi_seg_list).iteritems(),key=lambda asd:asd[1],reverse=True)
    
    logger_split_freq.info('c_zhusu_seg_list:')
    for item in c_zhusu_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_xianbingshi_seg_list:')
    for item in c_xianbingshi_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_jiwangshi_seg_list:')
    for item in c_jiwangshi_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_jiazushi_seg_list:')
    for item in c_jiazushi_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_quanshen_seg_list:')
    for item in c_quanshen_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_jiancha_seg_list:')
    for item in c_jiancha_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_zhenduan_seg_list:')
    for item in c_zhenduan_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))
    logger_split_freq.info('c_zhiliaojihua_seg_list:')
    for item in c_zhiliaojihua_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))  
    logger_split_freq.info('c_zhenduan_seg_list:')
    for item in c_chuzhi_seg_list:
        logger_split_freq.info(item[0].encode('utf-8')+' : \t'+str(item[1]))

def count_all_word():
    inpath='records'
    jieba.load_userdict("sources/concepts_dict.txt")
    words=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                sex=table.cell(i,1).value
                record=table.cell(i,5).value
                words.extend(jieba.lcut(record.strip().encode('utf-8')))
    sorted_word_freq=sorted(Counter(words).iteritems(),key=lambda asd:asd[1],reverse=True)
    for word_freq in sorted_word_freq:
        logger_word_freq.info(word_freq[0].encode('utf-8')+":\t"+str(word_freq[1]))

def analysis_seg(words):
    v_set=[]
    n_set=[]
    m_set=[]
    for word in words:
        if word.flag=='v':
            v_set.append(word.word)
        elif word.flag=='n':
            n_set.append(word.word)
        elif word.flag=='m':
            m_set.append(word.word)
    return v_set, n_set,m_set  
            
def part_seg():
    inpath='records'
    v_set_all=[]
    n_set_all=[]
    m_set_all=[]
    cnt=0
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=table.cell(i,5).value.encode('utf-8')
#                 print record
                try:
#                     print re.findall(r'主  诉：([\s\S]*)现病史',record)[0]
                    zhusu=re.findall(r'主  诉：([\s\S]*)现病史',record)[0].strip()
                    xianbingshi=re.findall(r'现病史：([\s\S]*)既往史',record)[0].strip()
                    jiwangshi=re.findall(r'既往史：([\s\S]*)家族史',record)[0].strip()
                    jiazushi=re.findall(r'家族史：([\s\S]*)全  身',record)[0].strip()
                    quanshen=re.findall(r'全  身：([\s\S]*)检  查',record)[0].strip()
                    jiancha=re.findall(r'检  查：([\s\S]*)诊断',record)[0].strip()
                    zhenduan=re.findall(r'诊断：([\s\S]*)治疗计划',record)[0].strip()
                    zhiliaojihua=re.findall(r'治疗计划：([\s\S]*)处 置',record)[0].strip()
                    chuzhi=re.findall(r'处 置：([\s\S]*)签名',record)[0].strip()
                    
                    #     jieba.load_userdict("sources/concepts_dict.txt")
                    jieba.load_userdict("sources/user_dict.txt")
#                     print cnt
                    
                    zhusu_seg_list = jieba.lcut(zhusu)
                    xianbingshi_seg_list = jieba.lcut(xianbingshi)
                    jiwangshi_seg_list = jieba.lcut(jiwangshi)
                    jiazushi_seg_list = jieba.lcut(jiazushi)
                    quanshen_seg_list = jieba.lcut(quanshen)
                    jiancha_seg_list = jieba.lcut(jiancha)
                    zhenduan_seg_list = jieba.lcut(zhenduan)
                    zhiliaojihua_seg_list = jieba.lcut(zhiliaojihua)
                    chuzhi_seg_list = jieba.lcut(chuzhi)
                    
#                     logger_test.info(' '.join([word.word+'/'+word.flag for word in postag.cut(zhusu)]))
                    
                    logger_zhusu.info(zhusu+'\n')
                    logger_zhusu.info(" ".join(zhusu_seg_list)+'\n')
                    logger_zhusu.info(' '.join([word.word+'/'+word.flag for word in postag.cut(zhusu)])+'\n~~~~~~~~~~~~~~~~~\n')

                    
                    v_set,n_set,m_set=analysis_seg(postag.cut(jiancha))
                    v_set_all.extend(v_set)
                    n_set_all.extend(n_set)
                    m_set_all.extend(m_set)
#                     print len(v_set_all)
                    filter_quanshen,filter_jiwangshi,filter_jiazushi=load_filter()
                    
                    logger_xianbingshi.info(xianbingshi+'\n')
                    logger_xianbingshi.info(" ".join(xianbingshi_seg_list)+'\n')
                    logger_xianbingshi.info(' '.join([word.word+'/'+word.flag for word in postag.cut(xianbingshi)])+'\n~~~~~~~~~~~~~~~~~\n')
                    if jiwangshi not in filter_jiwangshi:
                        logger_jiwangshi.info(jiwangshi+'\n')
                        logger_jiwangshi.info(" ".join(jiwangshi_seg_list)+'\n')
                        logger_jiwangshi.info(' '.join([word.word+'/'+word.flag for word in postag.cut(jiwangshi)])+'\n~~~~~~~~~~~~~~~~~\n')
                    if jiazushi not in filter_jiazushi:
                        logger_jiazushi.info(jiazushi+'\n')
                        logger_jiazushi.info(" ".join(jiazushi_seg_list)+'\n')
                        logger_jiazushi.info(' '.join([word.word+'/'+word.flag for word in postag.cut(jiazushi)])+'\n~~~~~~~~~~~~~~~~~\n')
                    if quanshen not in filter_quanshen:
                        logger_quanshen.info(quanshen+'\n')
                        logger_quanshen.info(" ".join(quanshen_seg_list)+'\n')
                        logger_quanshen.info(' '.join([word.word+'/'+word.flag for word in postag.cut(quanshen)])+'\n~~~~~~~~~~~~~~~~~\n')
                    logger_jiancha.info(jiancha+'\n')
                    logger_jiancha.info(" ".join(jiancha_seg_list)+'\n')
                    logger_jiancha.info(' '.join([word.word+'/'+word.flag for word in postag.cut(jiancha)])+'\n~~~~~~~~~~~~~~~~~\n')
                    logger_zhenduan.info(zhenduan+'\n')
                    logger_zhenduan.info(" ".join(zhenduan_seg_list)+'\n')
                    logger_zhenduan.info(' '.join([word.word+'/'+word.flag for word in postag.cut(zhenduan)])+'\n~~~~~~~~~~~~~~~~~\n')
                    logger_zhiliaojihua.info(zhiliaojihua+'\n')
                    logger_zhiliaojihua.info(" ".join(zhiliaojihua_seg_list)+'\n')
                    logger_zhiliaojihua.info(' '.join([word.word+'/'+word.flag for word in postag.cut(zhiliaojihua)])+'\n~~~~~~~~~~~~~~~~~\n')
                    logger_chuzhi.info(chuzhi+'\n')
                    logger_chuzhi.info(" ".join(chuzhi_seg_list)+'\n')
                    logger_chuzhi.info(' '.join([word.word+'/'+word.flag for word in postag.cut(chuzhi)])+'\n~~~~~~~~~~~~~~~~~\n')
                
                    cnt+=1
                except:
                    logger_exp.info(record)
                    logger_exp.info(traceback.format_exc())
                    
    logger_test.info('v_set_all: ')   
    for ele in sorted(Counter(v_set_all).iteritems(),key=lambda asd:asd[1],reverse=True):              
        logger_test.info(ele[0].encode('utf-8')+":"+str(ele[1]))
    logger_test.info('n_set_all: ')
    for ele in sorted(Counter(n_set_all).iteritems(),key=lambda asd:asd[1],reverse=True):              
        logger_test.info(ele[0].encode('utf-8')+":"+str(ele[1]))
    logger_test.info('m_set_all: ')
    for ele in sorted(Counter(m_set_all).iteritems(),key=lambda asd:asd[1],reverse=True):              
        logger_test.info(ele[0].encode('utf-8')+":"+str(ele[1]))   

def load_filter():
    filter_quanshen=codecs.open('sources/filter_quanshen.txt', 'r', 'utf-8')
    filter_jiwangshi=codecs.open('sources/filter_jiwangshi.txt', 'r', 'utf-8')
    filter_jiazushi=codecs.open('sources/filter_jiazushi.txt', 'r', 'utf-8')
    return [line.replace('\\n','\n').strip() for line in filter_quanshen.readlines()],\
        [line.replace('\\n','\n').strip() for line in filter_jiwangshi.readlines()],\
        [line.replace('\\n','\n').strip() for line in filter_jiazushi.readlines()]

def count_attribute():
    inpath='records'
    zhusu_all=[]
    xianbingshi_all=[]
    jiwangshi_all=[]
    jiazushi_all=[]
    quanshen_all=[]
    jiancha_all=[]
    zhenduan_all=[]
    zhiliaojihua_all=[]
    chuzhi_all=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=table.cell(i,5).value.encode('utf-8')
                try:
                    zhusu_all.append(re.findall(r'主\s*诉：([\s\S]*)现病史：',record)[0].strip())
                    xianbingshi_all.append(re.findall(r'现病史：([\s\S]*)既往史：',record)[0].strip())
                    jiwangshi_all.append(re.findall(r'既往史：([\s\S]*)家族史：',record)[0].strip())
                    jiazushi_all.append(re.findall(r'家族史：([\s\S]*)全\s*身：',record)[0].strip())
                    quanshen_all.append(re.findall(r'全\s*身：([\s\S]*)检\s*查：',record)[0].strip())
                    jiancha_all.append(re.findall(r'检\s*查：([\s\S]*)诊\s*断：',record)[0].strip())
                    zhenduan_all.append(re.findall(r'诊\s*断：([\s\S]*)治疗计划：',record)[0].strip())
                    zhiliaojihua_all.append(re.findall(r'治疗计划：([\s\S]*)处\s*置：',record)[0].strip())
                    chuzhi_all.append(re.findall(r'处\s*置：([\s\S]*)签名',record)[0].strip())
                    
                
                except:
                    logger_exp.info(record)
                    logger_exp.info(traceback.format_exc())
                    
#     jieba.load_userdict("sources/user_dict.txt")
    
    logger_attr.info("zhusu_all: %d" % len(Counter(zhusu_all)))              
    for item in sorted(Counter(zhusu_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~') 
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')  
    logger_attr.info("xianbingshi_all: %d" % len(Counter(xianbingshi_all)))                
    for item in sorted(Counter(xianbingshi_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~') 
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')
    logger_attr.info("jiwangshi_all: %d" % len(Counter(jiwangshi_all)))              
    for item in sorted(Counter(jiwangshi_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~') 
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')
    logger_attr.info("jiazushi_all: %d" % len(Counter(jiazushi_all)))               
    for item in sorted(Counter(jiazushi_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~') 
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')
    logger_attr.info("quanshen_all: %d" % len(Counter(quanshen_all)))              
    for item in sorted(Counter(quanshen_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~')
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n') 
    logger_attr.info("zhenduan_all: %d" % len(Counter(zhenduan_all)))             
    for item in sorted(Counter(zhenduan_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~')    
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')
    logger_attr.info("zhiliaojihua_all: %d" % len(Counter(zhiliaojihua_all)))              
    for item in sorted(Counter(zhiliaojihua_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~') 
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')
    logger_attr.info("jiancha_all: %d" % len(Counter(jiancha_all)))              
    for item in sorted(Counter(jiancha_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~')   
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')  
    logger_attr.info("chuzhi_all: %d" % len(Counter(chuzhi_all)))               
    for item in sorted(Counter(chuzhi_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_attr.info(item[0].encode('utf-8')+':\t'+str(item[1])+'\n~~~~~~~~~~~~~~~~~')
#         logger_attr.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')  
  
def you(zhusu):  
    zhusu_pos=postag.cut(zhusu)
    for word in zhusu_pos:
        if word.word=='有':
#             print zhusu_pos.next()
            return zhusu_pos.next().word

def special_record_path():
    inpath='records'
    pattern=r'|'.join([line.strip() for line in codecs.open('sources/remove_seg.txt','r','utf-8').readlines()]).replace('\\s','\s').encode('utf-8')
    jieba.load_userdict("sources/user_dict.txt")
    zhusu_all=[]
    chis=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=table.cell(i,5).value.encode('utf-8')
                zhusu=re.findall(r'主\s+诉：([\s\S]*)现病史',record)[0].strip()
                zhusu_clean=re.sub(pattern,'',zhusu)   
                s1=u'''旧充填体     牙色充填体，无龋坏，    叩痛（+++），I°松动。 牙龈缘轻度红肿，根尖区略红肿，颊侧无窦道口。冷测     冷测无反应。    X线片     X线片示：冠部 充填物高密度影近髓腔。 根管内 无充填物影像，根尖周根周膜增宽，近中、远中无牙槽骨吸收'''.encode('utf-8')
                if s1 in record:
                    print new_path.decode('gbk')
                    
                    
def detect_special_record():
    logger_zhusu_yaoqiu=log_file("zhusu_yaoqiu", "zhusu_yaoqiu_log")
    inpath='records'
    pattern=r'|'.join([line.strip() for line in codecs.open('sources/remove_seg.txt','r','utf-8').readlines()]).replace('\\s','\s').encode('utf-8')
    jieba.load_userdict("sources/user_dict.txt")
    zhusu_all=[]
    chis=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=table.cell(i,5).value.encode('utf-8')
#                 print chardet.detect(record).encode('utf-8')
#                 s1=u'左上前牙缺损数字个月'.encode('utf-8')
#                 print chardet.detect(r'主  诉')
                zhusu=re.findall(r'主\s+诉：([\s\S]*)现病史',record)[0].strip()
                
#                 if s1 in zhusu:
#                     print new_path.decode('gbk')
                zhusu_clean=re.sub(pattern,'',zhusu)
#                 yous.append(you(zhusu_clean))
#                 if chardet.detect(zhusu_clean)['encoding']!='utf-8':
#                     print zhusu_clean,chardet.detect(zhusu_clean)
#                 if zhusu_clean.startswith('要求'):
#                     p=r"要求(.*?)修复|口腔检查|拔除|治疗|改善|洗牙|洁牙|牙周检查|窝沟封闭|补牙|检查|洁治|修|拆除|复查|牙周维护|拆线|矫治|矫正|诊治|种植|拔出|充填|镶牙|牙齿美白|明确(.*?)设计方案"
#                     if len(re.findall(p, zhusu_clean))==0:
#                         zhusu_all.append(zhusu_clean)
                if  len(re.findall(r'要求|咨询', zhusu_clean))==0:
#                     p=r"要求(.*?)修复|口腔检查|拔除|治疗|改善|洗牙|洁牙|牙周检查|窝沟封闭|补牙|检查|洁治|修|拆除|复查|牙周维护|拆线|矫治|矫正|诊治|种植|拔出|充填|镶牙|牙齿美白|明确(.*?)设计方案"
#                     p1=r"(.*?)转诊"
#                     keshi.extend(re.findall(p, zhusu_clean))
#                 p1=r'(?<![洗拔坏缺补洁磨镶])牙(?![周齿不])'
#                 p2=r'(x|X|半|多|数|若干|一|二|两|三|四|五|六|七|八|九|十(来)*|１|３|４|６|\s*\d+\+*)\s*(个)*(年|月|周|日|天|小时)(余)*(左右)*|(\d+|一|十)\s*余\s*(年|月|周|日|天|小时)|月余'
#                 p2=r'(双|右|左|上|下|前|后|多)(.*)齿'
#                 if len(re.findall(p1, zhusu_clean))>0 and len(re.findall(p2, zhusu_clean))==0:
                    zhusu_all.append(zhusu_clean)
#                 if len(re.findall(p1, zhusu_clean))>0:
#                 p3=r'((双|右|左|上|下|前|后|多)(.*?)颌)'
#                 if len(re.findall(p3,zhusu_clean))>0:
# #                         print zhusu_clean
#                         chis.append((re.findall(p3,zhusu_clean.encode('utf-8'))[0][0]))
# #                         print re.findall(p3,zhusu_clean.encode('utf-8'))[0][0]
#     print len(chis)
#     for item in sorted(Counter(chis).iteritems(),key=lambda asd:asd[1], reverse=True):
#         if item[0]!=None:
#             logger_zhusu_yaoqiu.info(item[0])
                           
    logger_zhusu_yaoqiu.info("zhusu_all: %d" % len(Counter(zhusu_all))) 
    for item in sorted(Counter(zhusu_all).iteritems(),key=lambda asd:asd[1], reverse=True):
        logger_zhusu_yaoqiu.info(item[0].encode('utf-8')+':\t'+str(item[1])) 
#         logger_zhusu_yaoqiu.info(' '.join([word.word+'/'+word.flag for word in postag.cut(item[0])])+'\n~~~~~~~~~~~~~~~~~\n')  

def pre_process_jiancha(record):
    return re.sub('表格<诊断>内容:(:|\s+)*','',record)

def guanbu(jiancha):
    if len(re.findall('冠(.*?),',re.findall('临床邻牙检查[\s+邻牙：]*(.*?)[\r\n]', jiancha)[0]))==0 and \
    len(re.findall('(?<!牙)冠部(.*?)[，。；,;\r\n]',re.findall('[xX]线片示[：:]*(.*?)[\r\n]', jiancha)[0]))==0 and \
    len(re.findall('冠部(.*?)[，。；,;\r\n]',re.findall('[Xx]根尖片.*?：(.*?)\r', jiancha)[0]))==0 :
        return jiancha 
    else:
        return ''
        
        
def test_jiancha():                 
    logger_jiancha_research=log_file("jiancha_research.log", "logger_jiancha_research")
    inpath='records'
    pattern=r'|'.join([line.strip() for line in codecs.open('sources/remove_seg.txt','r','utf-8').readlines()]).replace('\\s','\s').encode('utf-8')
    jieba.load_userdict("sources/user_dict.txt")
    jiancha_all=[]
    chis=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=pre_process_jiancha(table.cell(i,5).value.encode('utf-8'))
                try:
                    jiancha=re.findall(r'检 \s*查\s*：([\s\S]*)诊\s*断\s*：',record)[0]
#                     jiancha_all.append(jiancha)[Xx]根尖片.*?：(.*?)[\r\n]
                    jiancha_all.append(guanbu(jiancha))
                    check_pattern='((([ⅠⅡⅢ]|I+)[度°]*[-~]([ⅠⅡⅢ]|I+)[度°]*)|([ⅠⅡⅢ]|I+|[123一二三])[+-]*[°度]*[+-]*[,；]*|[不无])松动'
                    check_pattern2='松动((([ⅠⅡⅢ]|I+)[度°]*[-~]([ⅠⅡⅢ]|I+)[度°]*)|([ⅠⅡⅢ]|I+|[123一二三])[+-]*[°度]*[+-]*[,；]*|[无])'
                    if len(re.findall(check_pattern, jiancha))==0 and len(re.findall(check_pattern2, jiancha))==0:
                        jiancha_all.append(jiancha)
#                         jiancha_all.append(re.findall(check_pattern, jiancha)[0])
#                     if len(re.findall('[xX]线片示[：]*(.*?)临床邻牙检查', jiancha))>0:
#                         jiancha_all.append(re.findall('[xX]线片示[：]*(.*?)临床邻牙检查', jiancha)[0])
#                     elif len(re.findall('[xX]线片示[：]*(.*?)邻牙', jiancha))>0:
#                         jiancha_all.append(re.findall('[xX]线片示[：]*(.*?)邻牙', jiancha)[0])
#                     elif len(re.findall('[xX]线片示[：]*(.*?)[\r\n]', jiancha))>0:
#                         jiancha_all.append(re.findall('[xX]线片示[：]*(.*?)[\r\n]', jiancha)[0])
#                     
                        
                except:
                    logger_exp.info(record)
                    logger_exp.info(traceback.format_exc())
    logger_jiancha_research.info("jiancha_all: %d" % len(Counter(jiancha_all))) 
    for item in sorted(Counter(jiancha_all).iteritems(),key=lambda asd:asd[1], reverse=True):
#         logger_jiancha_research.info(item[0].encode('utf-8')+'\n~~~~~~~~~~~~~~~~~~') 
        logger_jiancha_research.info(item[0]+'\n~~~~~~~~~~~~~~~~~~')
        #.encode('utf-8')
                   
if __name__ == '__main__':
#     inpath='records'
#     count_record()
#     medical_concept('concepts_all')
#     test_jiaba()
#     count_all_word()
#     test_jieba2()
#     test_record()
#     filter_oral_concepts()
#     merge_concept()
#     part_seg()
#     detect_special_record()
#     filter_segs()
#     count_attribute()
#     s1='要求修复双侧上后牙'
#     p3=r'((双|右|左|上|下|前|后|多)(.*?)牙)'
#     print re.findall(p3,s1.encode('utf-8'))[0][0]
#     special_record_path()
    test_jiancha()