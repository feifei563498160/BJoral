# -*- coding: utf-8 -*-
import os,django
import xlrd
os.environ.setdefault("DJANGO_SETTINGS_MODULE","kg_sys.settings")
django.setup()

from mosby.models import Drug
from bjoral.models import Record
import json
import re
import codecs

import sys
import traceback
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kg_sys.kg_sys.settings")
#sys.path.append(os.path.abspath(__file))
#print sys.path
#os.environ["DJANGO_SETTINGS_MODULE"]="kg_sys.settings"
#django.setup()

def get_ele(pattern,s1):
    m=re.search(pattern, s1)
    if m:
        return m.groupdict()['content']
    return ''

def put_record(inpath):
    cnt=0
    cnt_exp=0
    try:
        for rt, dirs, files in os.walk(inpath):
            for f in files:
                fname = os.path.splitext(f)
                new_path = inpath+os.sep+fname[0] + fname[1]
                data=xlrd.open_workbook(new_path)
                table=data.sheets()[0]
                nrows = table.nrows
                for i in range(2,nrows):
                    patientID=table.cell(i,0).value.encode('utf-8')
                    sex=table.cell(i,1).value.encode('utf-8')
                    birthday=table.cell(i,2).value.encode('utf-8')
                    medicalDate=table.cell(i,4).value.encode('utf-8')
                    record=table.cell(i,5).value.encode('utf-8')

                    zhusu=get_ele(r'主\s*诉：(?P<content>[\s\S]*)现病史：',record)
                    xianbingshi=get_ele(r'现病史：(?P<content>[\s\S]*)既往史：',record)
                    jiwangshi=get_ele(r'既往史：(?P<content>[\s\S]*)家族史：',record)
                    jiazushi=get_ele(r'家族史：(?P<content>[\s\S]*)全\s*身：',record)
                    quanshen=get_ele(r'全\s*身：(?P<content>[\s\S]*)检\s*查：',record)
                    jiancha=get_ele(r'检\s*查：(?P<content>[\s\S]*)诊\s*断：',record)
                    zhenduan=get_ele(r'诊\s*断：(?P<content>[\s\S]*)治疗计划：',record)
                    zhiliaojihua=get_ele(r'治疗计划：(?P<content>[\s\S]*)处\s*置：',record)
                    chuzhi=get_ele(r'处\s*置：(?P<content>[\s\S]*)签名',record)

                    Record.objects.get_or_create(patientID=patientID,sex=sex,birthday=birthday,medicalDate=medicalDate,\
                        record=record,zhusu=zhusu,xianbingshi=xianbingshi,jiwangshi=jiwangshi,jiazushi=jiazushi,\
                        quanshen=quanshen,jiancha=jiancha,zhenduan=zhenduan,zhiliaojihua=zhiliaojihua,chuzhi=chuzhi)
                    print "item: ",cnt,'OK'
                    cnt+=1
    except Exception:
        print "item: ",cnt ,'except'
        traceback.print_exc(Exception)
        cnt_exp+=1

def put_drug():
    in_path='items_drug.json'
    drug_itmes=json.load(codecs.open(in_path, encoding='UTF-8'))
    #drugs=[]
    cnt=0
    cnt_exp=0
    for item in drug_itmes:
        drug_name=item["concept"]
        meta_type='drug'
        for pos2def in item["pos2definition"]:
            try:
                attributes=pos2def["attributes"]
                if attributes.has_key("drugClass"):
                    drugClass=attributes["drugClass"]
                else:
                    drugClass=''
                if attributes.has_key("action"):
                    action=attributes["action"]
                else:
                    action=''
                if attributes.has_key("use"):    
                    use=attributes["use"]
                else:
                    use=''
                if attributes.has_key("brandName"):
                    brandName=attributes["brandName"]
                else:
                    brandName=''
            #drugs.append(Drug)

                
                cnt+=1
                drug_id=cnt
                Drug.objects.get_or_create(drug_name=drug_name,meta_type=meta_type,drugClass=drugClass,action=action,use=use,brandName=brandName)
                print "item: ",cnt,'OK'
            except Exception, e:
                print "item: ",cnt ,'except'
                traceback.print_exc()
                cnt_exp+=1
    print cnt,cnt_exp

def main():
    # sys.path.append(os.path.abspath(__file))
    # print sys.path

    # put_drug()
    in_path='records'
    put_record(in_path)

if __name__ == '__main__':
    main()
    print "Done"