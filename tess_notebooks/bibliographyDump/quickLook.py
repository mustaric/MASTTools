#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:02:19 2019

@author: smullally
"""

import pandas as p
import matplotlib.pyplot as plt
import datetime


all_file = "/Users/smullally/MASTBibliography/2019-08-22/papertrack_stats_by_entry_date_new.csv"
names = ['date','mission','type','count']
bibdata = p.read_csv(all_file, names = names, skiprows=1)

print(bibdata)

dti = p.to_datetime(bibdata['date'])

missions = set(bibdata['mission'])
print(missions)
#select_missions = ['PanSTARRS', 'GALEX', 'TESS',  'KEPLER', 'K2', 'IUE' ]
select_missions = ['HUT', 'Copernicus', 'EUVE', 'FIRST', 'BEFS', 'UIT', 'TUES', 'WUPPE', 'IMAPS', 'FUSE']
#%%
science = bibdata['type'] == 'SCIENCE'
mention = bibdata['type'] == 'MENTION'
influence = bibdata['type'] == 'DATA_INFLUENCED'

plt.figure(figsize=(10,10))

for m in select_missions:
    
    mission = bibdata['mission'] == m
    
    plt.subplot(311)
    plt.plot(dti[mission & science], bibdata['count'][mission & science],label=m)
    
    
    plt.subplot(312)
    plt.plot(dti[mission & mention], bibdata['count'][mission & mention], label=m)
    plt.title('Mention')
    
    plt.subplot(313)
    plt.plot(dti[mission & influence], bibdata['count'][mission & influence], label=m)
    plt.title('DATA_Influenced')
    
plt.subplot(311)
plt.title('Science')
plt.legend()
plt.subplot(312)
plt.title('mention')
plt.subplot(313)
plt.title('data influcned')
plt.legend()
plt.xlabel('ADS entry date')
plt.ylabel('paper counts per month')

plt.savefig('/Users/smullally/MASTBibliography/2019-08-22/newResultsAdsEntryMissionSmall.png')
    

#%%
#Correlations
select_missions = ['PanSTARRS', 'GALEX', 'TESS',  'KEPLER', 'K2', 'IUE', 'FUSE' ]
dates = set(dti[mission])

for m in select_missions:
    
    mission = bibdata['mission'] == m
    
    plt.plot(dates, )


#%%

plt.figure()

keplerpapers = (bibdata['type'] == 'SCIENCE') & (bibdata['mission'] == 'KEPLER')

plt.plot(dti[keplerpapers], bibdata['count'][keplerpapers],'o--',label='Kepler')

iuepapers = (bibdata['type'] == 'SCIENCE') & (bibdata['mission'] == 'IUE')

plt.plot(dti[iuepapers], bibdata['count'][iuepapers],'x-',label='IUE')

papers = (bibdata['type'] == 'SCIENCE') & (bibdata['mission'] == 'PanSTARRS')

plt.plot(dti[papers], bibdata['count'][papers],'s-',label='PanSTARRS')

mission = 'K2'
papers = (bibdata['type'] == 'SCIENCE') & (bibdata['mission'] == mission)
plt.plot(dti[papers], bibdata['count'][papers],'^-',label=mission)

mission = 'TESS'
papers = (bibdata['type'] == 'SCIENCE') & (bibdata['mission'] == mission)
plt.plot(dti[papers], bibdata['count'][papers],'^-',label=mission)
#plt.yscale('log')
plt.xlabel

plt.legend()
plt.title('Science Papers, New')