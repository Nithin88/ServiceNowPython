#!/usr/bin/python
import requests
import pandas as pd
import simplejson as json
import numpy as np
from pandas.io.json import json_normalize
import requests

'''
Execute Application/Cloud HealthCheck when P1 in queue
'''

class servicenow():
    def __init__(self):
        self.user=''
        self.pwd = '' 

    def getsev1url(self):
       '''
          Get incident with impact=1 & active=true
       '''
       url="https://[[your company servicenow url]]/api/now/table/incident?sysparm_query=assignment_group=[[group name]]&active=true&impact=1&sysparm_fields=number,u_event_details,active,impact,u_major_incident"
       return url

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

s=servicenow()
url=s.getsev1url()
df=s.getdf(url)
if not df.empty:
   ## Execute Cloud Healthcheck
   ## mail to group or append output to ticket
else:
   print "No P1 for ECS"
