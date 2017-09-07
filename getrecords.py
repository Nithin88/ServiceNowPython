#!/usr/bin/python
import requests
import pandas as pd
import sqlalchemy
import simplejson as json
import numpy as np
from pandas.io.json import json_normalize
import calendar
from threading import Thread

class servicenow():
    '''     
          Class to extract servicenow details for group in a month
          DB tables
                snow_info - task info of servicenow
                snow_taskbreachedsla  - breachedsla tickets
                snow_summary    - year & monthly summary of servicenow
                snow_textinfo  - short description & close notes
    ''' 
    def __init__(self,year,month):
        self.user=       #### servicenow user name
        self.pwd =       #### password
        temp,day=calendar.monthrange(year,month)
        self.startdate=str(year)+"-"+str(month)+"-1"
        self.enddate=str(year)+"-"+str(month)+"-"+str(day)


    def geturl(self):
        '''
           URL to get task ticket detils
        '''
        url="https://[[your servicenow url]]/api/now/table/task?sysparm_query=sys_created_onBETWEENjavascript:gs.dateGenerate('"+self.startdate+"','00:00:00')@javascript:gs.dateGenerate('"+self.enddate+"','23:59:59')&assignment_group=[[ servicenow assignment id ]]&sysparm_fields=number,short_description,caller_id.name,sys_created_by,impact,active,priority,closed_by,u_customer,made_sla,u_state,close_notes,sys_class_name,contact_type,sys_created_on"
        print url
        return url

    def getslaurl(self):
        '''
           URL to get SLA details
        '''
        url="https://[[your servicenow url]]/api/now/table/task_sla?sysparm_query=start_timeBETWEENjavascript:gs.dateGenerate('"+self.startdate+"','00:00:00')@javascript:gs.dateGenerate('"+self.enddate+"','23:59:59')&u_assignment_group=[[ servicenow assignment id ]]&stage=breached&sysparm_fields=task"
        print url
        return url

    def gettaskurl(self,taskid):
        '''
           URL to get task number and create date
        '''
        url="[[your servicenow url]]/api/now/table/task/"+str(taskid)+"?sysparm_fields=number,sys_created_on"
        return url

    def gettaskslatableurl(self,year,month):
        '''
           URL to get breached tickets
        '''
        temp,day=calendar.monthrange(year,month)
        startdate=str(year)+"-"+str(month)+"-1"
        enddate=str(year)+"-"+str(month)+"-"+str(day)
        url="https://[[your servicenow url]]/api/now/table/task_sla?sysparm_query=inc_sys_created_onBETWEENjavascript:gs.dateGenerate('"+startdate+"','00:00:00')@javascript:gs.dateGenerate('"+enddate+"','23:59:59')&u_assignment_group=[[ servicenow assignment id ]]&stage=breached"
        print url
        return url

    def insertdata(self,sql):
        #print "Insert SQL : {}".format(sql)
        try:
            [[ code to execute insert sql ]] 
        except Exception as e:
            print e.message, e.args
            print "Failed to execute {}".format(sql)

    def getdf(self,url):
       '''
            execute servicenow url to return dataframe 
       '''
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
    
    def getactive(self,df):
       '''
            return active ticket count
       '''
       val=df['active'].value_counts()
       print val
       if 'true' not in val:
             val['true']=0
       if 'false' not in val:
             val['false']=0
       return val

    def getincidents(self,df):
       '''
           return incident count
       '''
       val=df['sys_class_name'].value_counts()
       if not val['incident']:
             val['incident']=0
       if not val['sc_task']:
             val['sc_task']=0
       return val

def updatedata(year,month):
    s=servicenow(year,month)
    url=s.geturl()
    df=s.getdf(url)
    df.drop(['closed_by','closed_by.link','u_customer.link'], axis = 1, inplace = True, errors = 'ignore')
    df.rename(columns = {'closed_by.value':'closed_by','u_customer.value':'u_customer'},inplace=True)
    print df.head()
    df = df.fillna('')
    df['short_description']=df.short_description.str.encode('utf-8')
    df['close_notes']=df.close_notes.str.encode('utf-8')
    rep="(),')[]/-"
    for i in rep:
       df['short_description']=df['short_description'].str.replace(i,"")
       df['close_notes']=df['close_notes'].str.replace(i,"")
    print df.isnull().values.any()
    jobs=[]
    for index, row in df.iterrows():
       try:

    ######## sql to insert servicenow ticket details to DB
           sql="insert into snow_info (active, closed_by, contact_type, impact, made_sla, number, priority, sys_class_name, sys_created_by, sys_created_on, u_customer, u_state) VALUES('"+(row['active'])+"','"+str(row['closed_by'])+"','"+str(row['contact_type'])+"','"+str(row['impact'])+"','"+str(row['made_sla'])+"','"+str(row['number'])+"','"+str(row['priority'])+"','"+str(row['sys_class_name'])+"','"+str(row['sys_created_by'])+"','"+str(row['sys_created_on'])+"','"+str(row['u_customer'])+"','"+str(row['u_state'])+"')"
           p = Thread(target=s.insertdata, args=(sql,))
           jobs.append(p)
           p.start()

    ######### sql to insert servicenow ticket number,short description and close notes to DB
           sql="insert into snow_textinfo (number,short_description,close_notes) values ('"+str(row['number'])+"','"+str(row['short_description'])+"','"+str(row['close_notes'])+"')"
           p = Thread(target=s.insertdata, args=(sql,))
           jobs.append(p)
           p.start()
       except Exception as e:
           print e.message, e.args
           print "Failed to insert: {} {} {} {}".format(row['short_description'],row['close_notes'],row['sys_created_by'],row['sys_created_on'])
    for j in jobs:
        j.join()
    totaltasks=len(df.index)
    activecount=s.getactive(df)
    incidentcount=s.getincidents(df)
    print "Active: {} Inactive {}".format(activecount['true'],activecount['false'])
    print "Incident: {} Tasks {}".format(incidentcount['incident'],incidentcount['sc_task'])
    url=s.getslaurl()
    print url
    dfa=s.getdf(url)
    dfa.drop(['task.link'],inplace=True,axis=1,errors='ignore')    ## drop unused column
    print dfa
    breachedcount=len(dfa.index)

    ######## sql to insert servicenow SLA details to DB
    sql="insert into snow_summary (year,month,totaltasks,incidents,tasks,active,breachedsla)  VALUES("+str(year)+","+str(month)+","+str(totaltasks)+","+str(incidentcount['incident'])+","+str(incidentcount['sc_task'])+","+str(activecount['true'])+","+str(breachedcount)+")"
    s.insertdata(sql)

    dfa.rename(columns = {'task.value':'task'},inplace = True) ## rename task.value column name
    for index, row in dfa.iterrows():
        url=s.gettaskurl(row['task'])
        print url
        df=s.getdf(url)
        sql="insert into snow_taskbreachedsla (tasknumber,createdon) values ('"+df['number'].iloc[0]+"','"+df['sys_created_on'].iloc[0]+"')"
        try:
           s.insertdata(sql)
        except Exception as e:
           print e.message, e.args
           print "Failed to insert: {} {} {} {}".format(row['short_description'],row['close_notes'],row['sys_created_by'],row['sys_created_on'])

def main():
    year=  [[year to extract data ]]
    month= [[ month to extract data ]]
    updatedata(year,month)

if __name__ == "__main__":
    main()

