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
#     parse_json(item_res,attr_dict)
    
    prefix="http://www.semanticweb.org/ontolgies/bjoral/"
    
    
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

def json2rdf(dictlist):
     
     
     
def record2rdf(graphs,cnt_dict,record,patterns):

    jiancha_p=r'检\s*查：(?P<content>[\s\S]*)诊\s*断：'
    zhenduan_p=r'诊\s*断：(?P<content>[\s\S]*)治疗计划：'
    zhiliaojiahua_p=r'治疗计划：(?P<content>[\s\S]*)处\s*置：'

    jiancha_res=item2dict(graphs["jiancha"],cnt_dict["jiancha"],jiancha_p,"检查",record,patterns)
    zhenduan_res=item2dict(graphs["zhenduan"],cnt_dict["zhenduan"],zhenduan_p,"诊断",record,patterns)
    zhiliao_res=item2dict(graphs["zhiliao"],cnt_dict["zhiliao"],zhiliaojiahua_p,"检查",record,patterns)
    
    prefix=u"http://www.semanticweb.org/ontolgies/bjoral/"
    
    if jiancha_res!=None and zhenduan_res!=None:
        o1=rdflib.URIRef(prefix+u"关联")
        graphs["jiancha2zhenduan"].add((rdflib.URIRef(prefix+jiancha_res),o1,rdflib.URIRef(prefix+zhenduan_res)))
    if  zhiliao_res!=None and zhenduan_res!=None:  
        o2=rdflib.URIRef(prefix+u"关联")
        graphs["zhenduan2zhiliao"].add((rdflib.URIRef(prefix+zhenduan_res),o2,rdflib.URIRef(prefix+zhiliao_res)))
    

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



def records2rdf():
    inpath='records'
    patterns=json.load(codecs.open('sources/patterns.json', 'r', encoding='utf-8'))
    
    cnt=0
    jiacha_cnt=0
    zhenduan_cnt=0
    zhiliao_cnt=0
    chuzhi_cnt=0
    
    cnt_dict={}
    cnt_dict["jiancha"]=jiacha_cnt
    cnt_dict["zhenduan"]=zhenduan_cnt
    cnt_dict["zhiliao"]=zhiliao_cnt
    cnt_dict["chuzhi"]=chuzhi_cnt
    
    jiancha_graph=rdflib.Graph()
    zhenduan_graph=rdflib.Graph()
    zhiliao_graph=rdflib.Graph()
    chuzhi_graph=rdflib.Graph()
    
    jiancha2zhenduan_graph=rdflib.Graph()
    zhenduan2zhiliao_graph=rdflib.Graph()
    zhenduan2chuzhi_graph=rdflib.Graph()
    
    graphs={}
    graphs["jiancha"]=jiancha_graph
    graphs["zhenduan"]=zhenduan_graph
    graphs["zhiliao"]=zhiliao_graph
    graphs["chuzhi"]=chuzhi_graph
    graphs["jiancha"]=jiancha_graph
    graphs["jiancha2zhenduan"]=jiancha2zhenduan_graph
    graphs["zhenduan2zhiliao"]=zhenduan2zhiliao_graph
    graphs["zhenduan2chuzhi"]=zhenduan2chuzhi_graph
    
    
    
    for rt, dirs, files in os.walk(inpath):
        for f in files:
            fname = os.path.splitext(f)
            new_path = inpath+os.sep+fname[0] + fname[1]
            data=xlrd.open_workbook(new_path)
            table=data.sheets()[0]
            nrows = table.nrows
            for i in range(2,nrows):
                record=table.cell(i,5).value.encode('utf-8')
                record2rdf(graphs,cnt_dict,record,patterns)
                #record2rdf(record,chuzhi_graph,patterns)
                
                print cnt,cnt_dict["jiancha"],cnt_dict["zhenduan"],cnt_dict["zhiliao"]
                cnt+=1
    jiancha_graph.serialize("rdf/jiancha.rdf",encoding='utf-8') 
    zhenduan_graph.serialize("rdf/zhenduan.rdf",encoding='utf-8') 
    zhiliao_graph.serialize("rdf/zhiliao.rdf",encoding='utf-8') 
    chuzhi_graph.serialize("rdf/chuzhi.rdf",encoding='utf-8') 
    
    jiancha2zhenduan_graph.serialize("rdf/jiancha2zhenduan.rdf",encoding='utf-8') 
    zhenduan2zhiliao_graph.serialize("rdf/zhenduan2zhiliao.rdf",encoding='utf-8') 
    zhenduan2chuzhi_graph.serialize("rdf/zhenduan2chuzhi.rdf",encoding='utf-8')           
#                 jiancha=re.findall(r'检\s*查：([\s\S]*)诊\s*断：',record)[0].strip()
#                 zhenduan=re.findall(r'诊\s*断：([\s\S]*)治疗计划：',record)[0].strip()
#                 zhiliaojihua=re.findall(r'治疗计划：([\s\S]*)处\s*置：',record)[0].strip()
#                 chuzhi=re.findall(r'处\s*置：([\s\S]*)签名',record)[0].strip()
#                 
#                 jiancha_res=extract_attr_value_jiancha(jiancha,patterns["检查"])
#                 zhenduan_res=extract_attr_value_zhenduan(zhenduan,patterns["诊断"])
#                 #extract_attr_value_chuzhi()
#                 zhiliaojihua_res=extract_attr_value_zhiliao(zhiliaojihua,patterns["治疗计划"])
#                 
#                 jiancha_attr={}
#                 
#                 parse_json(jiancha_res)
#                 parse_json(zhenduan_res)
#                 parse_json(zhiliaojihua_res)
                
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
    
    s = rdflib.URIRef(prefix+'检查1')  
    p1 = rdflib.URIRef(prefix+'CBCT')  
    o1 = rdflib.URIRef(prefix+'CBCT1')
    
    s = rdflib.URIRef(prefix+'CBCT1')  
    p1 = rdflib.URIRef(prefix+'叩痛')  
    o1 = rdflib.URIRef(prefix+'2')
    
    s = rdflib.URIRef(prefix+'检查2')  
    p1 = rdflib.URIRef(prefix+'id')  
    o1 = rdflib.URIRef(prefix+'2')
    
    s2 = rdflib.URIRef(prefix+'诊断')  
    p2 = rdflib.URIRef(prefix+'疾病')  
    o2 = rdflib.URIRef(prefix+'死去')  
     
    s2 = rdflib.URIRef(prefix+'诊断')  
    p21 = rdflib.URIRef(prefix+'id')  
    o21 = rdflib.URIRef(prefix+'1') 
      
    g1 = rdflib.Graph()  
    g1.add((s, p, o))  
#     g1.add((s1, p1, o1))
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
    d1=  {
    "卫生状况": [
        "正常",
      "一般"
      
    ], 
    "修复体": [
      "全冠"
    ], 
    "牙冠": [
      "全冠"
    ], 
    "松动度": [
      "不"
    ], 
    "咬合": [
      "无明显异常"
    ], 
    "松动": [
      "全冠修复体不"
    ], 
    "CBCT": {
      "骨板": [
        "唇颊侧骨板完整厚度约1mm"
      ], 
      "骨质": [
        "骨质中等"
      ]
    }, 
    "叩痛": [
      "-"
    ]
  }
    d2={
    "卫生状况": [
      "一般",
      "正常"
    ], 
    "修复体": [
      "全冠"
    ], 
    "牙冠": [
      "全冠"
    ], 
    "松动度": [
      "不"
    ], 
    "咬合": [
      "无明显异常"
    ], 
    "松动": [
      "全冠修复体不"
    ], 
    "CBCT": {
      "骨板": [
        "唇颊侧骨板完整厚度约1mm"
      ], 
      "骨质": [
        "骨质中等"
      ]
    }, 
    "叩痛": [
      "-"
    ]
  }
    print d1==d2
    print dict_cmp(d1,d2)

if __name__ == '__main__':
#     test_rdf()
#     records2rdf()
    main()
 