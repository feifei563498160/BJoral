#coding=utf-8
'''
Created on 2016年12月7日

@author: feifei
'''

import os
import sys
import psycopg2
import time
from collections import Counter
import collections

class DB:
    
    def __init__(self,database="records", user="postgres", password="19920201", host="localhost", port="5432"):
        self.database=database
        self.user=user
        self.password=password
        self.host=host
        self.port=port
      
    def connectSQL(self):
        conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
        print "connection time: "+time.strftime('%Y-%m-%d;%H-%M-%S',time.localtime(time.time()))
        return conn

#     def operate(self,sql):
#         conn=self.connectSQL()
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         conn.commit()
#         conn.close()

def get_conn():
    return DB().connectSQL()

def test_sql():
    conn=DB().connectSQL()
    cursor=conn.cursor()
    nu="1000356431"
    sql="select * from bjoral_record where \"patientID\"=%s" % (nu)
    cursor.execute(sql)
    rows=cursor.fetchall()
    for row in rows:
        print row
        
    conn.commit()
    cursor.close()
    conn.close()
    
def test_sql2():
    conn=DB().connectSQL()
    cursor=conn.cursor()
    sql="select \"patientID\" from bjoral_record"
    cursor.execute(sql)
    rows=cursor.fetchall()
    l1=[]
    cnt=0
    for row in rows:
        if row[0] in l1:
            print row[0]
            cnt+=1
        else:
            l1.append(row[0])
#     print type(rows[0])
    print len(l1),cnt
    conn.commit()
    cursor.close()
    conn.close()
if __name__=='__main__':   

    test_sql()
    
    