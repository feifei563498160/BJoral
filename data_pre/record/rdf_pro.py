# -*- coding: utf-8 -*-
'''
Created on 2017��11��1��

@author: FeiFei
'''

#http://www.semanticweb.org/ontolgies/bjoral

import rdflib
import os,re
import codecs
import xlrd
import json

from collections import defaultdict

from data_pre.record.match import extract_attr_value_jiancha,\
    extract_attr_value_zhenduan, extract_attr_value_zhiliao
from util.string import parse_json
from util.mylogger import log_file

logger_jiancha=log_file("jiancha","jiancha")
logger_zhenduan=log_file("zhenduan", "zhenduan")
logger_zhenduan=log_file("zhiliao", "zhiliao")
#     cm=exist(attr_dict,graph)
#     if cm==False:
#         s_tmp=''
#         for attr,value in attr_dict.iteritems():
#             s=rdflib.URIRef(prefix+item+str(cnt))
#             p=rdflib.URIRef(prefix+attr)
#             o=rdflib.URIRef(prefix+value[0])
#             s_tmp=s
#             graph.add((s, p, o))
#         cnt+=1
#         return s_tmp
#     else:   
#         return cm[1]

        
# def dict2po(attr_dict):
#     poList=[]
#     prefix="http://www.semanticweb.org/ontolgies/bjoral/"
#     keys=attr_dict.keys()
#     keys.sort()
#     for key in keys:
#         poList.append((rdflib.URIRef(prefix+key),rdflib.URIRef(prefix+attr_dict.get(key)[0])))
#     return dict2po


# def exist(attr_dict,graph):
#     prefix="http://www.semanticweb.org/ontolgies/bjoral/"
#     keys=attr_dict.keys()
#     keys.sort()
#     for key in keys:
#         p=rdflib.URIRef(prefix+key)
#         o=rdflib.URIRef(prefix+attr_dict.get(key)[0])
#         
#         for subject in graph.subjects(p,o):
#             if dict2po(attr_dict)==list(graph.predicate_objects(subject)).sort():
#                 return (True,subject)
#     return False           
#             

def item2dict(graph,cnt,item_pattern,item,record,patterns):
    m=re.search(item_pattern, record)
    if m:
        item_content=m.groupdict()["content"]
    else:
        return
    
    if item=="检查":
        item_res=extract_attr_value_jiancha(item_content,patterns["jiancha"])
    elif item=="诊断":
        item_res=extract_attr_value_zhenduan(item_content,patterns["zhenduan"])
    elif item=="治疗计划":
        item_res=extract_attr_value_zhiliao(item_content,patterns["zhiliao"])
    return   item_res

          
def extract_attr_all(record,patterns):
    jiancha_p=r'检\s*查：(?P<content>[\s\S]*)诊\s*断：'
    zhenduan_p=r'诊\s*断：(?P<content>[\s\S]*)治疗计划：'
    zhiliaojiahua_p=r'治疗计划：(?P<content>[\s\S]*)处\s*置：'
    
    m1=re.search(jiancha_p, record)
    m2=re.search(zhenduan_p, record)
    m3=re.search(zhiliaojiahua_p, record)
    if m1 and m2 and m3:
        jiancha=m1.groupdict()["content"]
        zhendaun=m2.groupdict()["content"]
        zhiliao=m3.groupdict()["content"]
        jiancha_rel=extract_attr_value_jiancha(jiancha,patterns["jiancha"])
        zhendaun_rel=extract_attr_value_zhenduan(zhendaun,patterns["zhenduan"])
        zhiliao_rel=extract_attr_value_zhiliao(zhiliao,patterns["zhiliao"])
        return (jiancha_rel,zhendaun_rel,zhiliao_rel)
    else:
        return

def dict_cmp(dict1,dict2):
    if len(dict1)!=len(dict2):
        return False
    if dict1.keys()!=dict2.keys():
        return False
    for key in dict1.keys():
        if isinstance(dict1.get(key),list):
            if isinstance(dict2.get(key),list):
                if sorted(dict1.get(key))!=sorted(dict2.get(key)):
                    return False
            else:
                return False
        elif isinstance(dict1.get(key),dict):
            if isinstance(dict2.get(key),dict):
                if dict_cmp(dict1.get(key),dict2.get(key))==False:
                    return False
            else:
                return False
        elif isinstance(dict1.get(key),str) or isinstance(dict1.get(key),unicode):
            if isinstance(dict2.get(key),str) or isinstance(dict2.get(key),unicode):
                if dict1.get(key)!=dict2.get(key):
                    return False
            else:
                return False
        else:
            return False
    return True

def index_d(d1,l1):
    if len(l1)==0:
        return -1
    for i in range(len(l1)): 
        if dict_cmp(d1,l1[i]):
            return i
    return -1

def index_map(*results): 
    cnt=0   
    cnt_jiancha=-1
    cnt_zhenduan=-1
    cnt_zhiliao=-1
    jiancha_l=[]
    zhenduan_l=[]
    zhiliao_l=[]
    
    num_tup=[]
    for i in range(len(results[0])):
        if cnt>1000:
            break
        item=(results[0][i],results[1][i],results[2][i])
        tup=[]
        tup.append(cnt)
        jiancha_i=index_d(item[0],jiancha_l)
        zhenduan_i=index_d(item[1],zhenduan_l)
        zhiliao_i=index_d(item[2],zhiliao_l)
        if jiancha_i==-1:
            jiancha_l.append(item[0])
            cnt_jiancha+=1
            tup.append(cnt_jiancha)
        else:
            tup.append(jiancha_i)
        if zhenduan_i==-1:
            zhenduan_l.append(item[1])
            cnt_zhenduan+=1
            tup.append(cnt_zhenduan)
        else:
            tup.append(zhenduan_i)
        if zhiliao_i==-1:
            zhiliao_l.append(item[2])
            cnt_zhiliao+=1
            tup.append(cnt_zhiliao)
        else:   
            tup.append(zhiliao_i)
        num_tup.append(tup)
        print tup
        cnt+=1 
    return num_tup,jiancha_l,zhenduan_l,zhiliao_l

def extract_all_attr_dict():
    inpath='records'
    patterns=json.load(codecs.open('sources/patterns.json', 'r', encoding='utf-8'))
    
    results=[]
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=table.cell(i,5).value.encode('utf-8')
                res=extract_attr_all(record,patterns)
                if res!=None:
                    results.append(res)
                    
    jiancha_out="jiancha.json"               
    json.dump([item[0] for item in results], codecs.open(jiancha_out,'w','utf-8'),ensure_ascii=False,indent=2)
    
    zhenduan_out="zhenduan.json"
    json.dump([item[1] for item in results], codecs.open(zhenduan_out,'w','utf-8'),ensure_ascii=False,indent=2)
    
    zhiliao_out="zhiliao.json"
    json.dump([item[2] for item in results], codecs.open(zhiliao_out,'w','utf-8'),ensure_ascii=False,indent=2)
    print "attr extract over"

def dict2rdf(d1,item,index,graph):
    prefix=u"http://www.semanticweb.org/ontolgies/bjoral/"
    s=rdflib.URIRef(prefix+item+str(index))
    for key,value in d1.iteritems():
        p=rdflib.URIRef(prefix+key)
        if isinstance(value, list):
            for ele in value:
                if isinstance(ele, dict):
                    dict2rdf(ele,key,index,graph)
                elif isinstance(ele,str) or isinstance(ele,unicode):   
                    o=rdflib.URIRef(prefix+ele)
                    graph.add((s,p,o))
        elif isinstance(value, dict):
            dict2rdf(value,key,index,graph)

def list2rdf(l1,item,graph):
    for index,d1 in enumerate(l1):
        dict2rdf(d1,item,index,graph)
 
   
def records2rdf():
    jiancha_out="jiancha.json" 
    zhenduan_out="zhenduan.json"
    zhiliao_out="zhiliao.json"
    
    jiancha=json.load(codecs.open(jiancha_out,encoding="utf-8"))
    zhenduan=json.load(codecs.open(zhenduan_out,encoding="utf-8"))
    zhiliao=json.load(codecs.open(zhiliao_out,encoding="utf-8"))
    
    results=[jiancha,zhenduan,zhiliao]
    num_tup,jiancha_l,zhenduan_l,zhiliao_l=index_map(*results)
    
    jiancha_graph=rdflib.Graph()
    zhenduan_graph=rdflib.Graph()
    zhiliao_graph=rdflib.Graph()
#     list2rdf(jiancha_l,"检查",jiancha_graph)
    list2rdf(zhenduan_l,"诊断",zhenduan_graph)
#     list2rdf(zhiliao_l,"治疗计划",zhiliao_graph)
    
    jiancha2zhenduan_graph=rdflib.Graph()
    zhenduan2zhiliao_graph=rdflib.Graph()
#     zhenduan2chuzhi_graph=rdflib.Graph()
    
    for tup in num_tup:
        prefix=u"http://www.semanticweb.org/ontolgies/bjoral/"
        s=rdflib.URIRef(prefix+"检查"+str(tup[1]))
        p=rdflib.URIRef(prefix+"关联")
        o=rdflib.URIRef(prefix+"诊断"+str(tup[2]))
        jiancha2zhenduan_graph.add((s,p,o))
        
        s1=rdflib.URIRef(prefix+"诊断"+str(tup[2]))
        p1=rdflib.URIRef(prefix+"关联")
        o1=rdflib.URIRef(prefix+"治疗计划"+str(tup[3]))
        zhenduan2zhiliao_graph.add((s1,p1,o1))
        
    jiancha_graph.serialize("rdf/jiancha.rdf",encoding='utf-8') 
    zhenduan_graph.serialize("rdf/zhenduan.rdf",encoding='utf-8') 
    zhiliao_graph.serialize("rdf/zhiliao.rdf",encoding='utf-8') 
#     chuzhi_graph.serialize("rdf/chuzhi.rdf",encoding='utf-8') 
    
    jiancha2zhenduan_graph.serialize("rdf/jiancha2zhenduan.rdf",encoding='utf-8') 
    zhenduan2zhiliao_graph.serialize("rdf/zhenduan2zhiliao.rdf",encoding='utf-8') 
                
def test_rdf():
    
    jiacha_cnt=0
    zhenduan_cnt=0
    
    cnt_dict={}
    cnt_dict["jiancha"]=jiacha_cnt
    cnt_dict["zhenduan"]=zhenduan_cnt
    
    cnt_dict["jiancha"]+=1
    cnt_dict["zhenduan"]+=1
    
    print jiacha_cnt,zhenduan_cnt,cnt_dict["jiancha"],cnt_dict["zhenduan"]
    
    graph = rdflib.Graph()  
  
#     s = rdflib.URIRef('牛膝')  
#     p = rdflib.URIRef('功效属性')  
#     o = rdflib.URIRef('活血')  
#       
#     graph.add((s, p, o))  
#     # 以n3格式存储  
#     graph.serialize('zhongyao.rdf', format='n3')  
    prefix=u'http://www.semanticweb.org/ontolgies/bjoral/'
    
    s = rdflib.URIRef(prefix+'检查')  
    p = rdflib.URIRef(prefix+'叩痛')  
    o = rdflib.URIRef(prefix+'-')  
    
    s1 = rdflib.URIRef(prefix+'检查')  
    p1 = rdflib.URIRef(prefix+'叩痛')  
    o1 = rdflib.URIRef(prefix+'+')  
    

      
    g1 = rdflib.Graph()  
    g1.add((s, p, o))  

    g1.add((s1, p1, o1))
    g1.serialize('zhongyao1.rdf') # 默认以'xml'格式存储  
      
    g2 = rdflib.Graph()  
    g2.parse('zhongyao1.rdf', format='xml') # 解析rdf文件时，需要指定格式  
#     
    
#     print c1==c2
#     q=""
#     x = g2.query(q)  
#     print list(x) 
#     print list(g2.all_nodes())
    subject = g2.subjects(p, o)  
    
    fill=u'无限'
    pre=rdflib.term.URIRef((u'http://www.semanticweb.org/ontolgies/bjoral/%s' % (fill)))
    for item in g2.predicate_objects(pre):
        print item
    
    for i in subject:  
        for item in g2.predicate_objects(i):
            print item

        fill=u'无限'
        pre=rdflib.term.URIRef((u'http://www.semanticweb.org/ontolgies/bjoral/%s' % (fill)))
        for item in g2.predicate_objects(pre):
            print item

def main():
 
#     print d1==d2
#     print dict_cmp(d1,d2)
    pass

if __name__ == '__main__':
#     extract_all_attr_dict()
#     test_rdf()
    records2rdf()
#     main()
 