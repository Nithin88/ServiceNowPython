# ServiceNowPython

Repo contains python scripts written for ServiceNow integration. Project includes collecting ServiceNow data (CMDB & incidents) through API and report 
monthly task/incident SLA acheivement, CMDB inventory cross checks with cloudstack data, tasks tickets trends and 
frequent used words in incident short_description or closed_notes to identify patterns

## getrecords.py 
Collect data from ServiceNow task & incident details. Data updated to tables:
              *  snow_info - task info of servicenow
              *  snow_taskbreachedsla  - breachedsla tickets
              *  snow_summary    - year & monthly summary of servicenow
              *  snow_textinfo  - short description & close notes
                
## cloudstack_snow_cmdb_check.py
Collect CMDB inventory data for particular group/domain from ServiceNow. Maps CMDB & cloudstack inventory and report if any mismatch identified.

## servicenowkeywordanayzer.py
Analyze keywords in servicenow description & close notes collected with getrecords.py. Use wordcount python module perform basic AI to analyse
text. Data presented with image & text size projection using alice_color.png
