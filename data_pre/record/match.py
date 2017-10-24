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
from util.string import rep_start_dup
import traceback

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
        shichang=match_ele_zhusu(patterns["zhusu"]["shichang"],"shichang",clause.encode('utf-8'))
        keshi=match_ele_zhusu(patterns["zhusu"]["keshi"],"keshi",clause.encode('utf-8'))
        weizhi=match_ele_zhusu(patterns["zhusu"]["weizhi"],"weizhi",clause.encode('utf-8'))
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
            
def match_ele_zhusu(patterns,item,clause):
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
                 


def match_ele_jiancha(patterns,item,jiancha):
    for pattern in patterns:
        m=re.search(pattern, jiancha)
        if m:
            if item in ['zhongxian','heti','chicaozuo','yayin']:
                return  m.groupdict()  #包含 shang  和 xia
            else:
                return m.groupdict()['content']
    return ''       

def index_self(s1,l1):
    for i in range(len(l1)):
        if s1 in l1[1]:
            return i
    return -1
    
def get_start_end(part,whole):
    if part=='':
        return (-1,-1)
    pl=part.splitlines()
    wl=whole.splitlines()
    if pl[0]=='':
        return (index_self(pl[1],wl),index_self(pl[-1],wl))
    else:
        return (index_self(pl[0],wl),index_self(pl[-1],wl))
    
    
def extract_attr_value_jiancha(jiancha,patterns,sources):
    '''
                对检查按行split是合理的，经过人工统计暂没发现跨行的属性
    '''
#     lines=re.split('[\r\n]', jiancha)
    attr2value=defaultdict(list)
    print "jiancha: ",jiancha
    xxpjc=match_ele_jiancha(patterns["Xxianpianjiancha"]["self"],"Xxianpianjiancha",jiancha)
    if xxpjc!='':
        for line in re.split('[\r\n]', xxpjc):
            line=rep_start_dup(line).decode('utf-8')
            xxpgmx=match_ele_jiancha(patterns["Xxianpianjiancha"]["gumianxing"],"gumianxing",line)
            
            xxpgmdc=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["self"],"qumianduanceng",line)
            if xxpgmdc!='':
                xxpgycg=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["yacaogu"],"yacaogu",line)
                xxpgke=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["ke"],"ke",line)
                xxpgyp=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["yapei"],"yapei",line)
                xxpgmc=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["mengchu"],"mengchu",line)
                xxpgzs=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["zusheng"],"zusheng",line)
                xxpgtlcw=match_ele_jiancha(patterns["Xxianpianjiancha"]["qumianduanceng"]["yalie"],"yalie",line)
            
            xxptlcw=match_ele_jiancha(patterns["Xxianpianjiancha"]["toulucewei"]["self"],"toulucewei",line)
            if xxptlcw!='':
                xxptsxg=match_ele_jiancha(patterns["Xxianpianjiancha"]["toulucewei"]["shixianggu"],"shixianggu",line)
                xxptczg=match_ele_jiancha(patterns["Xxianpianjiancha"]["toulucewei"]["chuizhigu"],"chuizhigu",line)
                xxptqycqd=match_ele_jiancha(patterns["Xxianpianjiancha"]["toulucewei"]["qieyachunqingdu"],"qieyachunqingdu",line)
            
            xxpcbct=match_ele_jiancha(patterns["Xxianpianjiancha"]["CBCT"]["self"],"CBCT",line)
            if xxpcbct!='':
                xxpcke=match_ele_jiancha(patterns["Xxianpianjiancha"]["CBCT"]["ke"],"ke",line)
                xxpcgz=match_ele_jiancha(patterns["Xxianpianjiancha"]["CBCT"]["guzhi"],"guzhi",line)
             
            xxptlzw=match_ele_jiancha(patterns["Xxianpianjiancha"]["touluzhengwei"],"touluzhengwei",line)   
    
    lines=re.split('[\r\n]', jiancha)
    pos=get_start_end(xxpjc,jiancha)
    if pos[0]==-1:
        end=len(lines)
    else:
        end=pos[0]
    for line in lines[:end]:
        line=rep_start_dup(line).decode('utf-8')
        mczcjc=match_ele_jiancha(patterns["mengchuzhichijiancha"]["self"],"mengchuzhichijiancha",line)
        if mczcjc!='':
            mjcwz=match_ele_jiancha(patterns["mengchuzhichijiancha"]["jianchaweizhi"],"jianchaweizhi",line)
            mygwx=match_ele_jiancha(patterns["mengchuzhichijiancha"]["yaguanwaixing"],"yaguanwaixing",line)
            mguan=match_ele_jiancha(patterns["mengchuzhichijiancha"]["guan"],"guan",line)
            mkt=match_ele_jiancha(patterns["mengchuzhichijiancha"]["koutong"],"koutong",line)
            msdd=match_ele_jiancha(patterns["mengchuzhichijiancha"]["songdongdu"],"songdongdu",line)
            msyy=match_ele_jiancha(patterns["mengchuzhichijiancha"]["yayin"],"myayin",line)
            mfgym=match_ele_jiancha(patterns["mengchuzhichijiancha"]["fugaiyamian"],"fugaiyamian",line)
            mgz=match_ele_jiancha(patterns["mengchuzhichijiancha"]["guanzhou"],"guanzhou",line)
            mgs=match_ele_jiancha(patterns["mengchuzhichijiancha"]["qusun"],"qusun",line)
       
        xxps=match_ele_jiancha(patterns["Xxianpianshi"]["self"],"Xxianpianshi",line)
        if xxps!='':
            xxgs=match_ele_jiancha(patterns["Xxianpianshi"]["genshu"],"genshu",line)
            xxxz=match_ele_jiancha(patterns["Xxianpianshi"]["xingzhuang"],"xingzhuang",line)
            xxgb=match_ele_jiancha(patterns["Xxianpianshi"]["guanbu"],"guanbu",line)
            xxyggmf=match_ele_jiancha(patterns["Xxianpianshi"]["yaguangumaifu"],"yaguangumaifu",line)
            xxwz=match_ele_jiancha(patterns["Xxianpianshi"]["weizhi"],"weizhi",line)
            xxgjz=match_ele_jiancha(patterns["Xxianpianshi"]["genjianzhou"],"genjianzhou",line)
            xxycg=match_ele_jiancha(patterns["Xxianpianshi"]["yacaogu"],"yacaogu",line)
            xxggn=match_ele_jiancha(patterns["Xxianpianshi"]["genguannei"],"genguannei",line)
            xxqs=match_ele_jiancha(patterns["Xxianpianshi"]["queshi"],"queshi",line)
        
        qmdc=match_ele_jiancha(patterns["qumianduanceng"]["self"],"qumianduanceng",line)
        if qmdc!='':
            qgjz=match_ele_jiancha(patterns["qumianduanceng"]["genjianzhou"],"genjianzhou",line)
            qczql=match_ele_jiancha(patterns["qumianduanceng"]["chuizhiguliang"],"chuizhiguliang",line)
            qycg=match_ele_jiancha(patterns["qumianduanceng"]["yacaogu"],"yacaogu",line)
            qgj=match_ele_jiancha(patterns["qumianduanceng"]["genjian"],"genjian",line)
            qgs=match_ele_jiancha(patterns["qumianduanceng"]["genshu"],"genshu",line)
            qycjd=match_ele_jiancha(patterns["qumianduanceng"]["yacaojiding"],"yacaojiding",line)
            qshd=match_ele_jiancha(patterns["qumianduanceng"]["shanghedou"],"shanghedou",line)
            qwszk=match_ele_jiancha(patterns["qumianduanceng"]["weishengzhuangkuang"],"weishengzhuangkuang",line)
            
        lcly=match_ele_jiancha(patterns["linchuanglinya"]["self"],"linchuanglinya",line)
        if lcly!='':
            lkt=match_ele_jiancha(patterns["linchuanglinya"]["koutong"],"koutong",line)
            lguan=match_ele_jiancha(patterns["linchuanglinya"]["guan"],"guan",line)
            lsdd=match_ele_jiancha(patterns["linchuanglinya"]["songdongdu"],"songdongdu",line)
            lyy=match_ele_jiancha(patterns["linchuanglinya"]["yayin"],"lyayin",line)
            lctt=match_ele_jiancha(patterns["linchuanglinya"]["chongtianti"],"chongtianti",line)
            lqsun=match_ele_jiancha(patterns["linchuanglinya"]["qusun"],"qusun",line)
            lqshi=match_ele_jiancha(patterns["linchuanglinya"]["queshi"],"queshi",line)
            
        lxgjp=match_ele_jiancha(patterns["Xgenjianpian"]["self"],"Xgenjianpian",line)
        if lxgjp!='':
            xggb=match_ele_jiancha(patterns["Xgenjianqu"]["guanbu"],"guanbu",line)
            xggcyx=match_ele_jiancha(patterns["Xgenjianqu"]["genchongyingxiang"],"genchongyingxiang",line)
            xggjyx=match_ele_jiancha(patterns["Xgenjianqu"]["genjianyingxiang"],"genjianyingxiang",line)
            xgycg=match_ele_jiancha(patterns["Xgenjianqu"]["yacaogu"],"yacaogu",line)
                
        wszk=match_ele_jiancha(patterns["weishengzhuangkuang"],"weishengzhuangkuang",line)
        yy=match_ele_jiancha(patterns["yayin"],"yayin",line)

        gjz=match_ele_jiancha(patterns["genjianqu"],"genjianqu",line)
        yg=match_ele_jiancha(patterns["yaguan"],"yaguan",line)
        sdd=match_ele_jiancha(patterns["songdongdu"],"songdongdu",line)
        sd=match_ele_jiancha(patterns["songdong"],"songdong",line)
        qs=match_ele_jiancha(patterns["queshi"],"queshi",line)
        qz=match_ele_jiancha(patterns["guanzhou"],"guanzhou",line)
        ycg=match_ele_jiancha(patterns["yacaogu"],"yacaogu",line)
        ys=match_ele_jiancha(patterns["yashi"],"yashi",line)
        xft=match_ele_jiancha(patterns["xiufuti"],"xiufuti",line)
        pd=match_ele_jiancha(patterns["PD"],"PD",line)
        al=match_ele_jiancha(patterns["AL"],"AL",line)
        bi=match_ele_jiancha(patterns["BI"],"BI",line)
        kkd=match_ele_jiancha(patterns["kaikoudu"],"kaikoudu",line)
        ss=match_ele_jiancha(patterns["sesu"],"sesu",line)
        yh=match_ele_jiancha(patterns["yaohe"],"yaohe",line)
        jb=match_ele_jiancha(patterns["junban"],"junban",line)
        rg=match_ele_jiancha(patterns["ruangou"],"ruangou",line)
        kt=match_ele_jiancha(patterns["koutong"],"koutong",line)
        yhlx=match_ele_jiancha(patterns["yaheleixing"],"yaheleixing",line)
        mylx=match_ele_jiancha(patterns["moyaleixing"],"moyaleixing",line)
        qyfyh=match_ele_jiancha(patterns["qianyafuyahe"],"qianyafuyahe",line)
        qyfg=match_ele_jiancha(patterns["qianyafugai"],"qianyafugai",line)
        ylyj=match_ele_jiancha(patterns["yalieyongji"],"yalieyongji",line)
        ygkd=match_ele_jiancha(patterns["yagongkuandu"],"yagongkuandu",line)
        zyhqx=match_ele_jiancha(patterns["zongyahequxian"],"zongyahequxian",line)
        zx=match_ele_jiancha(patterns["zhongxian"],"zhongxian",line)
        ht=match_ele_jiancha(patterns["heti"],"heti",line)
        ccz=match_ele_jiancha(patterns["chicaozuo"],"chicaozuo",line)
        
        
        mb=match_ele_jiancha(patterns["mianbu"]["self"],"mianbu",line)
        if mb!='':
            mbdc=match_ele_jiancha(patterns["mianbu"]["duicheng"],"duicheng",line)
            mbmz=match_ele_jiancha(patterns["mianbu"]["mianzhong"],"mianzhong",line)
            mbmx=match_ele_jiancha(patterns["mianbu"]["mianxia"],"mianxia",line)
            mbhcg=match_ele_jiancha(patterns["mianbu"]["haichungou"],"haichungou",line)
            mbkclc=match_ele_jiancha(patterns["mianbu"]["kaichunlouchi"],"kaichunlouchi",line)
            mblywx=match_ele_jiancha(patterns["mianbu"]["louyinweixiao"],"louyinweixiao",line)
            mbhw=match_ele_jiancha(patterns["mianbu"]["hewo"],"hewo",line)
            
        cbct=match_ele_jiancha(patterns["CBCT"]["self"],"CBCT",line)
        if cbct!='':
            cbghd=match_ele_jiancha(patterns["CBCT"]["guhoudu"],"guhoudu",line)
            cbgb=match_ele_jiancha(patterns["CBCT"]["guban"],"guban",line)
            cbggd=match_ele_jiancha(patterns["CBCT"]["gugaodu"],"gugaodu",line)
            cbgz=match_ele_jiancha(patterns["CBCT"]["guzhi"],"guzhi",line)
    
        
        if xxpjc!='':
            xxpjc_dict=defaultdict(list)
            if xxpgmx!='':
                xxpjc_dict.append(xxpgmx)
            if xxpgmdc!='':
                xxpgmdc_dict=defaultdict(list)
                if xxpgycg!='':
                    xxpgmdc_dict["牙槽骨"].append(xxpgycg)
                if xxpgke!='':
                    xxpgmdc_dict["髁"].append(xxpgke)
                if xxpgyp!='':
                    xxpgmdc_dict["牙胚"].append(xxpgyp)
                if xxpgmc!='':
                    xxpgmdc_dict["萌出"].append(xxpgmc)
                if xxpgzs!='':
                    xxpgmdc_dict["阻生"].append(xxpgzs)
                if xxpgtlcw!='':
                    xxpgmdc_dict["牙列"].append(xxpgtlcw)
                xxpjc_dict["曲面断层"].append(xxpgmdc_dict)
            if xxptlcw!='':
                xxptlcw_dict=defaultdict(list)
                if xxptsxg!='':
                    xxptlcw_dict["矢向骨型"].append(xxptsxg)
                if xxptczg!='':
                    xxptlcw_dict["垂直骨型"].append(xxptczg)
                if xxptqycqd!='':
                    xxptlcw_dict["切牙唇倾度"].append(xxptqycqd)
                xxpjc_dict["头颅侧位"].append(xxptlcw_dict)
            if xxpcbct!='':
                xxpcbct_dict=defaultdict(list)
                if xxpcke!='':
                    xxpcbct_dict["髁"].append(xxpcke)
                if xxpcgz!='':
                    xxpcbct_dict["骨质"].append(xxpcgz)
                xxpjc_dict["CBCT"].append(xxpcbct_dict)
            if xxptlzw!='':
                xxpjc_dict["头颅正位"].append(xxptlzw) 
            attr2value["X线片检查"].append(xxpjc_dict)
        if mczcjc!='':
            mczcjc_dict=defaultdict(list)
            if mjcwz!='':
                mczcjc_dict["检查位置"].append(mjcwz)
            if mygwx!='':
                mczcjc_dict["牙冠外形"].append(mygwx)
            if mguan!='':
                mczcjc_dict["冠"].append(mguan)
            if mkt!='':
                mczcjc_dict["叩痛"].append(mkt)
            if msdd!='':
                mczcjc_dict["松动度"].append(msdd)
            if msyy!='':
                mczcjc_dict["牙龈"].append(msyy)
            if mfgym!='':
                mczcjc_dict["覆盖牙面"].append(mfgym)
            if mgz!='':
                mczcjc_dict["冠周"].append(mgz)
            if mgs!='':
                mczcjc_dict["龋损"].append(mgs)
            attr2value["萌出智齿检查"].append(mczcjc_dict)
        if xxps!='':
            xxps_dict=defaultdict(list)
            if xxgs!='':
                xxps_dict["根数"].append(xxgs)
            if xxxz!='':
                xxps_dict["形状"].append(xxxz)
            if xxgb!='':
                xxps_dict["冠部"].append(xxgb)
            if xxyggmf!='':
                xxps_dict["牙冠骨埋伏"].append(xxyggmf)
            if xxwz!='':
                xxps_dict["位置"].append(xxwz)
            if xxgjz!='':
                xxps_dict["根尖周"].append(xxgjz)
            if xxycg!='':
                xxps_dict["牙槽骨"].append(xxycg)
            if xxggn!='':
                xxps_dict["根管内"].append(xxggn)
            if xxqs!='':
                xxps_dict["缺失"].append(xxqs)
            attr2value["X线片示"].append(xxps_dict)
        if qmdc!='':
            qmdc_dict=defaultdict(list)
            if qgjz!='':
                qmdc_dict["根尖周"].append(qgjz)
            if qczql!='':
                qmdc_dict["垂直骨量"].append(qczql)
            if qycg!='':
                qmdc_dict["牙槽骨"].append(qycg)
            if qgj!='':
                qmdc_dict["根尖"].append(qgj)
            if qgs!='':
                qmdc_dict["根数"].append(qgs)
            if qycjd!='':
                qmdc_dict["牙槽嵴顶"].append(qycjd)
            if qshd!='':
                qmdc_dict["上颌窦"].append(qshd)
            if qwszk!='':
                qmdc_dict["卫生状况"].append(qwszk)
            attr2value["曲面断层"].append(qmdc_dict)   
        if lcly!='':
            lcly_dict=defaultdict(list)
            if lkt!='':
                lcly_dict["叩痛"].append(lkt)
            if lguan!='':
                lcly_dict["冠"].append(lguan)
            if lsdd!='':
                lcly_dict["松动度"].append(lsdd)
            if lyy!='':
                lcly_dict["牙龈"].append(lyy)
            if lctt!='':
                lcly_dict["充填体"].append(lctt)
            if lqsun!='':
                lcly_dict["龋损"].append(lqsun)
            if lqshi!='':
                lcly_dict["缺失"].append(lqshi)      
            attr2value["临床邻牙检查"].append(lcly_dict) 
        if lxgjp!='':
            lxgjp_dict=defaultdict(list)
            if xggb!='':
                lxgjp_dict["冠部"].append(xggb)
            if xggcyx!='':
                lxgjp_dict["根充影像"].append(xggcyx)
            if xggjyx!='':
                lxgjp_dict["根尖影像"].append(xggjyx)
            if xgycg!='':
                lxgjp_dict["牙槽骨"].append(xgycg)   
            attr2value["X根尖区"].append(lxgjp_dict)   
        if mb!='':
            mb_dict=defaultdict(list)
            if mbdc!='':
                lxgjp_dict["对称"].append(mbdc)  
            if mbmz!='':
                lxgjp_dict["面中"].append(mbmz) 
            if mbmx!='':
                lxgjp_dict["面下"].append(mbmx) 
            if mbhcg!='':
                lxgjp_dict["唇沟"].append(mbhcg) 
            if mbkclc!='':
                lxgjp_dict["开唇露齿"].append(mbkclc) 
            if mblywx!='':
                lxgjp_dict["露龈微笑"].append(mblywx) 
            if mbhw!='':
                lxgjp_dict["颏窝"].append(mbhw)      
            attr2value["面部"].append(mb_dict)
        if cbct!='':
            cbct_dict=defaultdict(list)
            if cbghd!='':
                cbct_dict["骨厚度"].append(cbghd)
            if cbgb!='':
                cbct_dict["骨板"].append(cbgb) 
            if cbggd!='':
                cbct_dict["骨高度"].append(cbggd) 
            if cbgz!='':
                cbct_dict["骨质"].append(cbgz)        
            attr2value["CBCT"].append(cbct_dict)
        if len(yy)!=0:
            if yy.has_key("content"):
                attr2value["牙龈"].append(yy["content"])
            else:
                yy_dict=defaultdict(list)
                yy_dict["颜色"].append(yy["yanse"])
                yy_dict["质地"].append(yy["zhidi"])
                yy_dict["形态"].append(yy["xingtai"])
                attr2value["牙龈"].append(yy_dict)
        if wszk!='':
            attr2value["卫生状况"].append(wszk)
        if gjz!='':
            attr2value["根尖区"].append(gjz)
        if yg!='':
            attr2value["牙冠"].append(yg)
        if sdd!='':
            attr2value["松动度"].append(sdd)
        if sd!='':
            attr2value["松动"].append(sd)
        if qs!='':
            attr2value["缺失"].append(qs)
        if qz!='':
            attr2value["冠周"].append(qz)
        if ycg!='':
            attr2value["牙槽骨"].append(ycg)
        if ys!='':
            attr2value["牙石"].append(ys)
        if xft!='':
            attr2value["修复体"].append(xft)
        if pd!='':
            attr2value["PD"].append(pd)
        if al!='':
            attr2value["AL"].append(al)
        if bi!='':
            attr2value["BI"].append(bi)
        if kkd!='':
            attr2value["开口度"].append(kkd)
        if ss!='':
            attr2value["色素"].append(ss)
        if yh!='':
            attr2value["咬合"].append(yh)
        if jb!='':
            attr2value["菌斑"].append(jb)
        if rg!='':
            attr2value["软垢"].append(rg)  
        if kt!='':
            attr2value["叩痛"].append(kt) 
        if yhlx!='':
            attr2value["牙合类型"].append(yhlx) 
        if mylx!='':
            attr2value["磨牙类型"].append(mylx) 
        if qyfyh!='':
            attr2value["前牙覆牙合"].append(qyfyh) 
        if qyfg!='':
            attr2value["前牙覆盖"].append(qyfg) 
        if ylyj!='':
            attr2value["牙列拥挤"].append(ylyj) 
        if ygkd!='':
            attr2value["牙弓宽度"].append(ygkd) 
        if zyhqx!='':
            attr2value["纵牙合曲线"].append(zyhqx)    
        if len(zx)!=0:
            if zx.has_key("content"):
                attr2value["中线"].append(zx["content"])
            else:
                zx_dict=defaultdict(list)
                zx_dict["上"].append(zx["shang"])
                zx_dict["下"].append(zx["xia"])
                attr2value["中线"].append(zx_dict)
        if len(ht)!=0:
            if ht.has_key("content"):
                attr2value["颌体"].append(ht["content"])
            else:
                ht_dict=defaultdict(list)
                ht_dict["上"].append(ht["shang"])
                ht_dict["下"].append(ht["xia"])
                attr2value["颌体"].append(ht_dict)
        if len(ccz)!=0:
            if ccz.has_key("content"):
                attr2value["齿槽座"].append(ccz["content"])
            else:
                ccz_dict=defaultdict(list)
                ccz_dict["上"].append(ccz["shang"])
                ccz_dict["下"].append(ccz["xia"])
                attr2value["齿槽座"].append(ccz_dict)
    attr2value["jiancha"].append(jiancha)
    return attr2value

def match_ele_zhenduan(patterns,zhenduan):
    for pattern in patterns:
        m=re.search(pattern, zhenduan)
        if m:
            return  m.groupdict()  
    return []

def get_zhenduan_beizhu(s1):
    beizhu=[]
    if u'?' in s1: 
        beizhu.append(u'?')
    if u'？' in s1:
        beizhu.append(u'？')
    result=re.findall(u"([(（]+(.*?)[)）]+)", s1)
    if len(result)!=0:
        for ele in result:
            beizhu.append(ele[1])
    
    jibing=re.sub(u"([(（]+(.*?)[)）]+)|[?？]", u"", s1)
    if len(beizhu)!=0:
        return {"疾病":jibing,"备注":beizhu}
    else:
        return {"疾病":jibing}

def extract_attr_value_zhenduan(zhenduan,patterns,sources):
    attr2value=defaultdict(list)
    for line in re.split(u'[\n\r]+', zhenduan):
        if line.strip()=='':
            continue
        if '；' in line:
            for ele in line.split('；'):
                attr2value["诊断"].append(get_zhenduan_beizhu(ele))
        anshi=match_ele_zhenduan(patterns["anshi"],line)
        guxing=match_ele_zhenduan(patterns["guxing"],line)
        maoshi=match_ele_zhenduan(patterns["maoshi"],line)
        duozhenduan=match_ele_zhenduan(patterns["duozhenduan"],line)
        if len(anshi)!=0:
            attr2value["诊断"].append(get_zhenduan_beizhu(anshi.groups(0)))
        if len(guxing)!=0:
            attr2value["诊断"].append(get_zhenduan_beizhu(guxing.groups(0)))
        if len(maoshi)!=0:
            attr2value["诊断"].append(get_zhenduan_beizhu(maoshi.groups(0)))
        if len(duozhenduan)!=0:
            for value in duozhenduan.values():
                attr2value["诊断"].append(get_zhenduan_beizhu(value))
        if len(anshi)==0 and len(guxing)==0 and len(maoshi)==0 and len(duozhenduan)==0:
            attr2value["诊断"].append(get_zhenduan_beizhu(line.strip()))
    attr2value["诊断"].append({"record":zhenduan})
    return  attr2value  


def match_ele_zhiliao(patterns,zhenduan):
    for pattern in patterns:
        m=re.search(pattern, zhenduan)
        if m:
            return  m.groupdict()["content"]
    return ''

def contain(s1,li):
    for ele in li:
        if s1 in ele:
            return True
    return False

def filter_xuzhi(zhiliao):
    xuzhis=[u"成人矫治须知",
            u"口腔卫生差须知",
            u"牙周病须知",
            u"TMD须知",
            u"矫治过程中可能出现的问题",
            u"正畸正颌联合治疗须知",
            u"涉及外伤牙的正畸治疗须知",
            u"牙根短须知",
            u"埋伏/阻生牙的牵引须知",
            u"骨性III类早期矫治须知",
            u"开合须知",
            u"唇腭裂患者须知",
            u"中重度骨性畸形掩饰性治疗(单纯正畸治疗)须知"]
    tag_line_num=[]
    zhiliao_l=re.split(u'[\n\r]+',zhiliao)
    for i in range(len(zhiliao_l)):
        if zhiliao_l[i].strip()=='':
            continue
        for xuzhi in xuzhis:
            if xuzhi in zhiliao_l[i]:
                tag_line_num.append(i)
                break
    if len(tag_line_num)==0:
        return zhiliao
    return u'\n'.join(zhiliao_l[:min(tag_line_num)])

def get_left_content(fangan1,fangan2,fangan3,zhiliao):
    
    if fangan3=='' and fangan2=='' and fangan2=='':
        return zhiliao
    start=-1
    end=-1
    pos3=get_start_end(fangan3,zhiliao)
    pos2=get_start_end(fangan2,zhiliao)
    pos1=get_start_end(fangan1,zhiliao)
    
    end=max([pos1[1],pos2[1],pos3[1]])
    start=pos1[0]
    left_content='\n'.join(zhiliao.splitlines()[:start]+zhiliao.splitlines()[end+1:])
#     print left_content
    return left_content

def extract_attr_value_zhiliao(zhiliao_origin,patterns,sources):
    attr2value=defaultdict(list)
    zhiliao=filter_xuzhi(zhiliao_origin)
    fangan3=match_ele_zhiliao(patterns["fangan"]["fangan3"],zhiliao)
    fangan2=match_ele_zhiliao(patterns["fangan"]["fangan2"],zhiliao)
    fangan1=match_ele_zhiliao(patterns["fangan"]["fangan1"],zhiliao)
    if fangan3!='':
        fangan3_dict=defaultdict(list)
        for line in fangan3.splitlines():
            if line.strip()=='':
                continue
            fangan3_dict["方案三"].append(match_ele_zhiliao(patterns["fangan"]["hang"],line))
        attr2value["治疗方案"].append(fangan3_dict)
    if fangan2!='':
        fangan2_dict=defaultdict(list)
        for line in fangan2.splitlines():
            if line.strip()=='':
                continue
            fangan2_dict["方案二"].append(match_ele_zhiliao(patterns["fangan"]["hang"],line))
        attr2value["治疗方案"].append(fangan2_dict)
    if fangan1!='':
        fangan1_dict=defaultdict(list)
        for line in fangan1.splitlines():
            if line.strip()=='':
                continue
            fangan1_dict["方案一"].append(match_ele_zhiliao(patterns["fangan"]["hang"],line))
        attr2value["治疗方案"].append(fangan1_dict)
    
    left_content=get_left_content(fangan1,fangan2,fangan3,zhiliao)
    xzfa=match_ele_zhiliao(patterns["xuanzefangan"],left_content)
    zlgc=match_ele_zhiliao(patterns["zhiliaoguocheng"],left_content)
    fy=match_ele_zhiliao(patterns["jiaozhifeiyong"]["feiyong"],left_content)
    fybz=match_ele_zhiliao(patterns["jiaozhifeiyong"]["beizhu"],left_content)
    if  xzfa!='':  
        attr2value["选择方案"].append(xzfa)
    if  zlgc!='':  
        attr2value["治疗过程"].append(zlgc)
    if  fy!='':  
        attr2value["费用"].append(fy)
    if  fybz!='':  
        attr2value["费用备注"].append(fybz)    
        
    if fangan3=='' and fangan2=='' and fangan2=='':
        for line in zhiliao.splitlines():
            if line.strip()=='':
                continue
            if match_ele_zhiliao(patterns["duofangan"],line)!='':
                fangan=[]
                for ele in re.split(u'\d*\.', line):
                    if ele.strip()!='':
                        fangan.append(ele.strip())
                attr2value["方案"].extend(fangan)
            elif match_ele_zhiliao(patterns["danfangan"],line)!='':
                attr2value["方案"].append(match_ele_zhiliao(patterns["danfangan"],line))
    
    attr2value["record_origin"].append(zhiliao_origin)
    attr2value["record"].append(zhiliao)
    return attr2value
   
def process_records(inpath,pattern_path):
    patterns=json.load(codecs.open(pattern_path, 'r', encoding='utf-8'))
    jieba.load_userdict("sources/user_dict.txt")
    wenti=[line.strip() for line in codecs.open("sources/zhusu/wenti.txt", 'r', encoding='utf-8').readlines()]
    sources=[]
    sources.append(wenti)
    zhusus_attr=[]
    jiancha_attr=[]
    zhenduan_attr=[]
    zhiliao_attr=[]
    cnt=0
    try:
        for rt, dirs, files in os.walk(inpath):
                for f in files:
                    fname = os.path.splitext(f)
                    new_path = inpath+os.sep+fname[0] + fname[1]
                    data=xlrd.open_workbook(new_path)
                    table=data.sheets()[0]
                    nrows = table.nrows
                    for i in range(2,nrows):
                        record=table.cell(i,5).value.encode('utf-8')
    #                     zhusu=re.findall(r'主\s*诉：([\s\S]*)现病史',record)[0].strip()
    #                     zhusus_attr.append(extract_attr_value_zhusu(zhusu,patterns,sources))
                        try:
#                             jiancha=re.findall(r'检\s*查：([\s\S]*)诊\s*断：',record)[0].strip()
#                             zhenduan=re.findall(r'诊\s*断：([\s\S]*)治疗计划：',record)[0].strip()
                            zhiliao=re.findall(r'治疗计划：([\s\S]*)处\s*置：',record)[0].strip()
                            if zhiliao.strip()=='':
                                continue
                        except Exception:
                            continue
#                         result=extract_attr_value_jiancha(jiancha, patterns["jiancha"], sources)
#                         result=extract_attr_value_zhenduan(zhenduan, patterns["zhenduan"], sources)
                        result=extract_attr_value_zhiliao(zhiliao, patterns["zhiliao"], sources)
#                         print json.dumps(result,ensure_ascii=False)
#                         jiancha_attr.append(result)
#                         zhenduan_attr.append(result)
                        zhiliao_attr.append(result)
                        cnt+=1
#     json.dump(zhusus_attr, codecs.open("zhusus_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
    except Exception:
        traceback.print_exc(Exception)
        print zhiliao
        json.dump(zhiliao_attr, codecs.open("zhiliao_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
    print cnt
    json.dump(zhiliao_attr, codecs.open("zhiliao_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
    
#         json.dump(zhenduan_attr, codecs.open("zhenduan_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
#     json.dump(zhenduan_attr, codecs.open("zhenduan_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
         
#         json.dump(jiancha_attr, codecs.open("jiancha_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
#     json.dump(jiancha_attr, codecs.open("jiancha_attr.json", 'w','utf-8'),ensure_ascii=False,indent=2)
#             
def debug_record():
#     zhusu='牙周治疗后定期复查'
    patterns=json.load(codecs.open('sources/patterns.json', 'r', encoding='utf-8'))
    sources=[]
#     extract_attr_value_zhusu(zhusu,patterns,sources)
    
    zhiliao=u'''方案一:正畸+正颌联合治疗
    1.拔除
    2.直丝弓矫治器
    3.排齐前牙调整牙轴。
      4.正颌手术解决颌间关系不调。
   5.牙槽突植骨欠丰满，根尖1/3处骨缺损，正畸排齐后有可能该牙出现松动或不能保留情况。患者可以考虑再次植骨。
   6.滞留，牙根完整，位于根方，颊舌向水平阻生，CT示牙根发育不佳，根短，位置低。暂时观察，可以考虑拔除保留。
方案二:
    1.暂时不考虑正颌治疗，唇侧固定矫治
    2.开展牙弓，创造缺失牙间隙，正畸治疗完成后修复缺牙。
    3.牙槽突植骨处骨质欠丰满，正畸治疗中可能出现牙齿松动不能保留，治疗后需修复治疗。
    4.患者仍处于生长发育快速期，如果下颌生长量较大，则仍不排除正颌手术可能。
5.滞留，牙根完整，位于根方，颊舌向水平阻生，CT示牙根发育不佳，根短，位置低。暂时观察，可以考虑拔除保留。

矫治疗程:大约3年
矫治费用:21750元，不含进口矫治器和种植体费用
经与患者协商，现选择方案二
矫治过程中可能出现的问题：
            1.戴用固定矫正器的患者要特别注意口腔卫生。
        2.矫正过程中必须按照医嘱定期复诊。
    3.患者18岁之前均处于生长发育期，若颌骨生长型异常，治疗结果则难以令人满意，异常生长在保持期还可表现为畸形复发，严重的发育异常可能需要结合外科手术进一步治疗。
    4.现代医学研究发现，正畸患者的颞下颌关节病（TMD）发病率与普通人群的TMD发病率相同，因此一般认为常规正畸治疗既不会引起也不能阻止TMD的发生。
    5.正畸治疗过程中有可能会出现非正畸医生所能控制的意外情况如牙根吸收、牙髓坏死等，少数患者的牙齿可能由于存在难以发现的根骨粘连而无法移动，以致无法完成治疗计划。
    6.成年患者常伴发牙周组织炎症而在正畸治疗中或治疗后出现较明显的牙龈组织退缩，易在牙齿颈部尤其前牙间出现小的三角间隙。
    7.治疗完成后需戴用保持器2年左右，少数患者需要更长时间，甚至终生保持，以防复发。
    详见《口腔正畸科治疗须知》
                                      患者签字：'''
    zhiliao_attr=[]
    line=u"缺失，牙槽嵴吸收严重，位点可见种植体，封闭螺丝在，表面软垢较多，种植体舌侧黏膜暗红、轻度肿胀。  有明显过长，牙龈退缩明显，松动I度。"
    
#     print match_ele_jiancha(patterns["jiancha"]["songdongdu"],"songdongdu",line)
    zhiliao_attr.append(extract_attr_value_zhiliao(zhiliao, patterns["zhiliao"], sources))
    print json.dumps(zhiliao_attr,ensure_ascii=False)
    json.dump(zhiliao_attr, codecs.open("zhiliao_attr_test.json", 'w','utf-8'),ensure_ascii=False,indent=2)
#     
def main():
    inpath='records'
    pattern_path='sources/patterns.json'
    process_records(inpath,pattern_path)

if __name__ == '__main__':
    main()
#     debug_record()
