# -*- coding: utf-8 -*-
'''
Created on 2017��9��30��

@author: FeiFei
'''

import sys
import os
import xlrd
import jieba
import codecs
import re
import json

from collections import defaultdict
import chardet
from util.mylogger import log_file

reload(sys)
sys.setdefaultencoding('utf8') 

logger_error=log_file("log/log_error_zhusu", "chuzhi_error")


def pre_process_zhusu(zhusu):
    pattern=r'|'.join([line.strip() for line in codecs.open('sources/remove_seg.txt','r','utf-8').readlines()]).replace('\\s','\s').encode('utf-8')
    tmp1=re.sub('\s+','',re.sub(pattern,'',zhusu))
    if "要求" in zhusu and (zhusu.decode('utf-8').find(u'要求')>0 and zhusu.decode('utf-8').find(u'，要求')<0):
        return tmp1.replace("要求", "，要求")
    return tmp1
    #去除多余的重复表达
    
    #去除多余的空白符

def replace_split(sent):
    sent.replace('\\','\\\\')
    

def extract_attr_value_zhusu(zhusu,patterns,sources):
    zhusu_clean=pre_process_zhusu(zhusu)
    clauses=re.split('，|、|：|,',zhusu_clean)
#     wt=defaultdict(list)#问题
#     wz=defaultdict(list)#位置
#     ks=defaultdict(list)#转诊科室
#     sq=defaultdict(list)#诉求
#     zlxm=defaultdict(list)#治疗项目
#     zzsc=defaultdict(list)#症状时长
    attr2value=defaultdict(list)
    for clause in clauses:
        clause=re.sub("\s+|。|，", '', clause)
#         match_ele(patterns["zhusu"]["suqiu"],"suqiu",clause)
        shichang=match_ele(patterns["zhusu"]["shichang"],"shichang",clause.encode('utf-8'))
        keshi=match_ele(patterns["zhusu"]["keshi"],"keshi",clause.encode('utf-8'))
        weizhi=match_ele(patterns["zhusu"]["weizhi"],"weizhi",clause.encode('utf-8'))
        if clause.startswith("要求"):
            if weizhi=='':
                p="要求"+'(.*)'
                yqxm=re.findall(p, clause)[0]
                attr2value["诉求"].append("要求")
                attr2value["主诉项目"].append(yqxm)
            else:
                p="要求"+'(.*?)'+weizhi
                yqxm=re.findall(p, clause)[0]
                if yqxm=='':
                    p="要求"+weizhi+'(.*)'
                    yqxm=re.findall(p, clause)[0]
                attr2value["诉求"].append("要求")
                attr2value["主诉项目"].append(yqxm)
                attr2value["位置"].append(weizhi)
        elif clause.startswith("咨询"):
            p="咨询"+'(.*)'
            zxxm=re.findall(p, clause)[0]
            attr2value["诉求"].append("要求")
            attr2value["主诉项目"].append(zxxm)
        elif clause.startswith("发现"):
            p="发现"+'(.*)'
            zz=re.findall(p.replace('+','\+'), clause)[0]
            attr2value["症状"].append(zz)
        elif clause.startswith("同矫治设计"):
            attr2value["诉求"].append("同矫治设计")
        elif "定期" in clause:
            p="(.*?定期.*?(复查|口腔(健康)*检查|维护|检查))(.*)"
            suqiu=re.findall(p, clause)[0][0]
            attr2value["诉求"].append(suqiu)
            if re.findall(p, clause)[0][3]!='':
                attr2value["位置"].append(weizhi)    
        elif weizhi!='' and clause.startswith(weizhi):
            attr2value["位置"].append(weizhi)
            if shichang!='':
                p=weizhi+'(发现)*(.*?)'+shichang
                attr2value["发病时长"].append(shichang)
#             print clause
#             print weizhi,shichang,p
            else:
                p=weizhi+'(发现)*(.*)'
            zz=re.findall(p, clause)[0][1]
            attr2value["症状"].append(zz)
                
        elif keshi!='' and clause.startswith(keshi):
            p=keshi+'(转诊|转拔|转科|转入)'+'([\S]*)'
            zzxm=re.findall(p, clause)[0][1]#治疗项目
            attr2value["转诊科室"].append(keshi)
            if zzxm!='':
                attr2value["主诉项目"].append(zzxm)
        elif shichang!='':
            p='(.*)'+shichang
#             print p,p.replace('+','\+'),chardet.detect(p)
#             print clause,chardet.detect(clause)
#             print re.findall(p.replace('+','\+'), clause)
            zz=re.findall(p.replace('+','\+'), clause)[0]
            attr2value["症状"].append(zz)
            attr2value["发病时长"].append(shichang)
        elif clause in sources[0]:
            attr2value["症状"].append(clause)
        
            
    if len(attr2value)==0:
        attr2value["empty"]=''
        logger_error.info('record: %s' % zhusu_clean)
#         if record_clean=='。':
#             logger_error.info('record: %s' % record)
            
    attr2value["record"]=zhusu_clean 
     
    return attr2value     
            
def match_ele(patterns,item,clause):
    for pattern in patterns:
        
        if len(re.findall(pattern.encode('utf-8'), clause))==0:
            return ''
        result=re.findall(pattern.encode('utf-8'), clause)
#         print pattern
#         print result
        if item=="weizhi":
            if result[0]!='':
#                 attr[item].append(result[0][0])
                return result[0][0]
            elif result[5]!='':
                return result[0][5]
#                 attr[item].append(result[0][5])
            elif result[7]!='':
                return result[0][7]
#                 attr[item].append(result[0][7])
        elif item in ["suqiu"]:
            return result[0]
#             attr[item].append(result[0])
        elif item in ["shichang","keshi"]:
            return result[0][0]
#             attr[item].append(result[0][0])
                 
def process_records(inpath,pattern_path):
    patterns=json.load(codecs.open(pattern_path, 'r', encoding='utf-8'))
    jieba.load_userdict("sources/user_dict.txt")
    wenti=[line.strip() for line in codecs.open("sources/zhusu/wenti.txt", 'r', encoding='utf-8').readlines()]
    sources=[]
    sources.append(wenti)
    zhusus_attr=[]
    for rt, dirs, files in os.walk(inpath):
            for f in files:
                fname = os.path.splitext(f)
                new_path = inpath+os.sep+fname[0] + fname[1]
                data=xlrd.open_workbook(new_path)
                table=data.sheets()[0]
                nrows = table.nrows
                for i in range(2,nrows):
                    record=table.cell(i,5).value.encode('utf-8')
                    zhusu=re.findall(r'主\s*诉：([\s\S]*)现病史',record)[0].strip()
                    zhusus_attr.append(extract_attr_value_zhusu(zhusu,patterns,sources))
                    
    json.dump(zhusus_attr, codecs.open("zhusus_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)

def debug_record():
    zhusu='牙周治疗后定期复查'
    patterns=json.load(codecs.open('sources/patterns.json', 'r', encoding='utf-8'))
    sources=[]
    extract_attr_value_zhusu(zhusu,patterns,sources)
    
    
def main():
    inpath='records'
    pattern_path='sources/patterns.json'
    process_records(inpath,pattern_path)

if __name__ == '__main__':
    main()
#     debug_record()
