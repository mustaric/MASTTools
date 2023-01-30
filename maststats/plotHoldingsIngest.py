#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:42:48 2018

@author: smullally

Read MAST Data and create a plot of holdings vs. time.
"""
import pandas as p
import numpy as np

import matplotlib.pyplot as plt

#%%
#Plot Holdings
hold_filename="/Users/smullally/Desktop/MASTData/holdings.xlsx"

#You canchange the the names, but don't change the order.
#Note it reads the dates as first of the month not last of the month.
colnames=["HST","GSC_I&II", "DSS","IUE","FUSE","VLA_FIRST","GALEX", "EUVE",\
          "Legacy", "XMM_OM","EPOCH","HLSP","Kepler/K2","HLA", "JWST_SI&T",\
          "SWIFTUVOT","PANSTARRS","SumPart","Date"]


units=1024  #Put 1024 if you want in Tb, or 1 if want in Gb

useCol=np.arange(0,19,1)

holddf=p.read_excel(hold_filename,sheet=0,skiprows=np.arange(0,25,1),\
                    names=colnames,usecols=useCol)

totalHoldings=holddf[colnames[0:17]].sum(axis=1)
holddf['Total'] = totalHoldings
mostHoldings=holddf[colnames[0:16]].sum(axis=1)
holddf['TotalNoPAN'] = mostHoldings
times=holddf.Date
holddf.set_index('Date',inplace=True,drop=False)


#%% Plot Holdings vs time for big ones and overall.

#Sort based on current holdings So I can just show the largest data sets.
sizes=holddf[colnames][holddf.Date=='2018-02-01'].as_matrix()
ind=np.argsort(sizes[0][0:17])
sortnames=list(map(lambda x: colnames[x], ind))
sortsizes=list(map(lambda x: sizes[0][x], ind))
#%%

def basicHoldingsPlot(holddf,plotnames,totalHoldings, units=1024, title=''):
    """
    Create the basic plot of the Holdings.
    """
#    if log:
#        tH=np.log10(totalHoldings/units)
#        df=(holddf[plotnames]/units).apply(np.log10)
#    else:
    tH=totalHoldings/units
    df=holddf[plotnames]
        
    for c in plotnames:            
        plt.plot(holddf.Date,df[c]/units,'-',linewidth=2,label=c)

    try:
        plt.plot(holddf.Date,tH,'k-',linewidth=3,label='Total')
    except (ValueError,TypeError):
        pass
    plt.legend(framealpha=.9)
    plt.xlabel('Date')
    
    if units==1024:
        plt.ylabel('MAST Holdings (Tb)')
    else:
        plt.ylabel('MAST Holdings (Gb)')

    plt.title(title)
    plt.tick_params(top='on',right='on',direction='in')
    plt.tick_params(which='minor',right='on',direction='in')

#Plot all and Total.
plt.figure(figsize=(8,6))
plotnames=sortnames[-5:]

basicHoldingsPlot(holddf,plotnames, holddf['Total'],units=units,title='Total MAST Holdings')

#%%
#Log Plot
plotnames=sortnames[-6:]
plt.figure(figsize=(10,6))
basicHoldingsPlot(holddf,plotnames,holddf['Total'],units=units,\
                  title='MAST Holdings: Largest Contributers')
#ax=plt.axes()
plt.gca().set_yscale("log")

#lab=np.logspace(0,4,5)
#strlab=list(map(lambda x: "%1.0e" % (x), lab))
#locat=np.log10(lab)
#plt.yticks(locat,strlab,fontsize=10)

#%%
#Plot All without PanStars
plotnames=sortnames[0:16]   
plt.figure(figsize=(8,6))
basicHoldingsPlot(holddf,plotnames,np.array([0,0]),units=units,\
                  title='MAST Holdings without PANSTARRS')


#plot area plot
plotnames=sortnames[0:17]
(holddf[plotnames]/units).plot.area(figsize=(8,6))
plt.title("All MAST Holdings")
    
#Plot as a stacked histogram
#plt.figure(figsize=(8,6))
#plt.hist(holddf[sortnames[0:16]])

#%%
#Explore the MAST Distribution Volumes.
#
dist_filename="/Users/smullally/Desktop/MASTData/ingest_dist-Feb2000Feb2018.xlsx"
distdf=p.read_excel(dist_filename,sheet=0)
distdf.rename(columns={"Distribution.1":"DistTb","Ingest.1":"IngestTb"},inplace=True)

#Get last month's largest volume ones
sizes=distdf[distdf.columns[0:-8]].loc['2018-02-01'].as_matrix()
ind=np.argsort(sizes)
sortnames=list(map(lambda x: distdf.columns[x], ind))
sortsizes=list(map(lambda x: sizes[x], ind))

#Simple plot of distribution each month
plt.figure(figsize=(9,7))
distdf['DistTb'].plot()
plt.ylabel('Data Volume (Tb) per month',fontsize=12)
plt.xlabel('Date',fontsize=12)
plt.title('MAST Data Distribution')

#
#%%
#Choose which columns to plot with plotnames
plotnames=sortnames[-7:]
distdf[plotnames].plot.area()
plt.ylabel('Tb/month')
plt.xlabel('Date')
t1 = p.to_datetime('2012-01-01')
t2 = p.to_datetime('2018-02-01')
plt.xlim(t1,t2)
plt.title("MAST Distribution for those with current largest distribution")

plotnames=sortnames[0:7]
distdf[plotnames].plot.area()
plt.ylabel('Tb/month')
plt.xlabel('Date')
t1 = p.to_datetime('2000-01-01')
t2 = p.to_datetime('2018-02-01')
plt.xlim(t1,t2)
plt.title("MAST Distribution for those with current smallest distribution")

#%%
#Pie Charts
def plotPie(holddf,date,colnames,limit=4):
    """
    For a particular date plot a pie chart of the holdings.
    holddf is the dataframe from the excel sheet
    date is a string like "2017-01-01" All should be the first day of month.
    colnames are those to include in the pie chart.
    limit is the smallest slice to show, these get grouped into one slice "other"
    """
    
    sizes=holddf[colnames][holddf.Date==date].as_matrix()
    total=holddf[holddf.Date==date].sum(axis=1)
    
    fraction=np.array(100*sizes[0]/float(total))

    keep=fraction>limit
    otherfrac=fraction[~keep].sum()
    ff=np.zeros(len(fraction)+1)
    ff[0:len(fraction)]=fraction[keep]

    ff[len(fraction)]=otherfrac
    print(keep)
    print(colnames)
    colnamesar=np.array(colnames)
    keepnames=colnamesar[keep]
    keepnames=list(keepnames).append("Other")
    

    plt.pie(ff,labels=keepnames,autopct='%1.1f%%',startangle=90)
    plt.tight_layout()
    

plt.figure()
plotPie(holddf,"2018-02-01",colnames[0:17])
