#!/usr/bin/python
import requests
import pandas as pd
import sqlalchemy
import simplejson as json
import numpy as np
from pandas.io.json import json_normalize
import calendar
from threading import Thread
import time

class servicenow():
    '''
        Compare ESX & Tintri Inventory Between
        ServiceNow CMDB & Cloudstack DB & update missing entries to reporting DB 
        Script assume hostname contains "ESX" & "Tintri" in hostname as identifier
    '''
    def __init__(self):
        self.user=''  ## ServiceNow Username
        self.pwd = '' ## ServiceNow password

    def geturl(self):
       url="https://[[servicenow URL ]]/api/now/table/cmdb_ci?sysparm_query=nameCONTAINSesx&sysparm_fields=operational_status,name"
       print url
       return url
    
    def gettintriurl(self):
       url="https://[[servicenow URL ]]/api/now/table/cmdb_ci?sysparm_query=nameCONTAINStintri&sysparm_fields=operational_status,name"
       print url
       return url

    def getcsesxdata(self):
       sql="select upper(substring_index(name,'.',1)) as name,status from cloud.host where removed is null and name like '%esx%'"
       cnxn= ## get connection for Cloudstack MySQL DB
       df = pd.read_sql_query(sql, cnxn) 
       return df

    def getcstintridata(self):
       sql="select upper(substring_index(host_address,'-',1)) as name,status from cloud.storage_pool where removed is null and upper(host_address) like '%TINTRI%'"
       cnxn= ## get connection for Cloudstack MySQL DB
       df = pd.read_sql_query(sql, cnxn)
       return df

    def insertdata(self,sql):
        #print "Insert SQL : {}".format(sql)
        try:
            [[ Execute SQL to update info to reporting DB ]]
        except Exception as e:
            print e.message, e.args
            print "Failed to execute {}".format(sql)

    def getdf(self,url):
       headers = {"Accept":"application/json"}
       response = requests.get(url, auth=(self.user, self.pwd), headers=headers )
       if response.status_code != 200:
         print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
         exit()
       #print('Status:',response.status_code,'Headers:',response.headers,'Response:',response.json())
       array = response.json()
       data=array["result"]
       df= json_normalize(data)
       return df

    def getsql(self,hostname,type,bool1,bool2):
      try:
          sql="insert into [[ reporting db ]] (hostname,cmdb,cloudstack,type) values ('"+str(hostname)+"','"+bool1+"','"+bool2+"','"+type+"')"
      except Exception as e:
          sql=""
          print e.message, e.args
          print "Failed to execute {}".format(sql)
      return sql 

    def esxcheck(self):
       c1=servicenow()
       url=c1.geturl()
       df=c1.getdf(url)
       df['name']=df['name'].str.upper()
       #print df.head()
       dfecs=c1.getcsesxdata()
       #print dfecs.head()
       dfa=pd.merge(dfecs,df,on='name',how='right')
       dfa=dfa[pd.isnull(dfa['status'])]
       #print dfa
       type="ESX"
       for index, row in dfa.iterrows():
           print row['operational_status']
           if row['operational_status']=='1':
               sql=c1.getsql(row['name'],type,"True","False")
               print sql
               c1.insertdata(sql)
       dfa=pd.merge(dfecs,df,on='name',how='left')
       dfa=dfa[pd.isnull(dfa['operational_status'])]
       for index, row in dfa.iterrows():
           sql=c1.getsql(row['name'],type,"False","True")
           print sql
           c1.insertdata(sql)

    def tintricheck(self):
       url=c1.gettintriurl()
       df=c1.getdf(url)
       df['name']=df['name'].str.upper()
       #print df.head()
       dfecs=c1.getcstintridata()
       #print dfecs.head()
       type="Tintri"
       dfa=pd.merge(dfecs,df,on='name',how='left')
       dfa=dfa[pd.isnull(dfa['operational_status'])]
       for index, row in dfa.iterrows():
           sql=c1.getsql(row['name'],type,"False","True")
           print sql
           c1.insertdata(sql)

def main()
    c1=servicenow()
    sql="delete from [[ reporting db table"  ## clear table for last checks
    [[ execute sql ]]
    c1.esxcheck()
    c1.tintricheck()

if __name__ == "__main__":
    main()

