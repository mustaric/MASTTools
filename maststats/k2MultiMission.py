#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 10:21:52 2017

@author: smullally

Create a histogram of the number of K2 targets in a campaign
that have other observations.
Can do this by project of filter or mission
"""

import sys
from tqdm import *
import re

import json
import mastAPITools as api

from astropy.table import Table
import numpy as np

from astropy.time import Time

import pprint
pp = pprint.PrettyPrinter(indent=4)

import pandas as p
import numpy as np

import matplotlib.pyplot as plt



def getEpicListByStart(startTime_iso,proj="K2"):
    """
    Filtered Query of Mast for a specific project
    with observations within .25 days of a known start time
    Intended for finding observations of one K2 campaign.
    Returns a list of epic ids
    """


    t=Time(startTime_iso,format='iso', scale='utc')
    tmjd=t.mjd
    
    requestFilters = [
                             {"paramName":"project",
                              "values":[proj],
                              "separator":";"
                             },
                             {"paramName":"t_min",
                              "values":[{"min":tmjd-.5 , "max":tmjd+.5}]
                              },
                         ]
    
    mashupRequest = {"service":"Mast.Caom.Filtered",
                     "format":"json",
                     "params":{
                         #"columns":"COUNT_BIG(*)",
                         "columns":"*",
                         "filters":requestFilters
                         }}
    
    headers,outString = api.mastQuery(mashupRequest)
    countData = json.loads(outString)
    pdata=p.DataFrame.from_dict(countData['data'])
    
    epicids=list(map(lambda x: x[4:13], pdata['obs_id']))
    
    return epicids

def getObservationDataframe(epicids,radius_arcsec=8):
    """
    Fill up a pandas dataframe with the list of interesting fields.
    """
    dataAvail=p.DataFrame()
    for k2id in epicids:
        #Cone Search each epicid
        targetName="EPIC %u" % np.int(k2id)
        mastData=api.targetNameConeSearch(targetName, radius_arcsec)
        data=p.DataFrame.from_dict(mastData['data'])
        newdata=p.concat([dataAvail,data],axis=0)
        dataAvail=newdata
        
    return dataAvail

def getUniqueObservations(targetName,radius_arcsec=8,columns=["obs_collection","project"]):
    """
    Get a list of unique information for one epicid.
    Ask for what observations exist. combine the requested columns of information
    then do a unique on that list.
    columns needs to have two elements, but they can be the same.
    """

    #Cone Search each epicid
    mastData=api.targetNameConeSearch(targetName, radius_arcsec)
    data=p.DataFrame.from_dict(mastData['data'])
    if len(data)>0:
        datatypelist=list(map( lambda x,y: "%s-%s" % (x,y), data[columns[0]],data[columns[1]] ) )
        uniquedatatypes=np.unique(datatypelist)
    else:
        uniquedatatypes=[]

    return uniquedatatypes

def plotUniqueCounts(names,counts):
    """
    Create a bar plot of the unique observations.
    
    """
    y_pos = np.arange(len(names))
    plt.bar(y_pos, counts, align='center', alpha=0.8)
    plt.xticks(y_pos, names,rotation=20)
    
    plt.xlabel('Types of Observations Available')
    plt.ylabel('Number of Targets with each Obs.')
    

def getK2NamesList(filename):
    """
    Read in NExScI csv file to get EPIC IDs.
    """
    data=np.loadtxt(filename,dtype=str,comments='#',delimiter=',',usecols=[1],skiprows=16)
    
    epicids=list(map ( lambda x: np.int(re.split(' ',x[2:-1])[1]), data ))
    
    return epicids
    
def getKeplerPlanets(filename):
    """
    filename is a nexsci csv list.
    returns list of kepids.
    """
    data=np.loadtxt(filename,dtype=str,comments='#',delimiter=',',usecols=[1],skiprows=1)
    
    epicids=list(map ( lambda x: np.int(x[2:-1]), data[1:] ))
    
    return epicids

def getHeartbeat(filename):
    """
    Use CSV file from villanova for heartbeatstar list
    """
    
    data=np.loadtxt(filename,dtype=int,comments='#',delimiter=',',usecols=[0])
    
    kepids=list(data)
    
    return kepids

def main():
    """ Main Function
        Set the start time of the campaign you are curious about.
    """
    
    #columns=["obs_id","project","filters","obs_collection","instrument_name","wavelength_region"]
    #starttime="2016-07-13 02:04:00"
    #starttime="2014-03-12 00:18:30"
    #This one is time intensive
    #epicids=getEpicListByStart(starttime,proj="K2")
    #epicids=getK2NamesList('/Users/smullally/K2/missioncount/k2names.csv')
    #epicids=getKeplerPlanets('/Users/smullally/Kepler/missioncount/kepler_confirmed.csv')
    epicids=getHeartbeat('/Users/smullally/Kepler/missioncount/heartbeatstars.csv')
    #print(len(epicids))
    #print(epicids[0:5])
    #print(epicids[-4:])
    
    i=0
    coneradius_arcsec=8  #arcseconds
    obspertarget=[]
    missing=[]
    for kid in tqdm(epicids):
        i=i+1
        #targetName="EPIC %u" % np.int(kid)
        targetName="KIC %u" % np.int(kid)
        uniqueObs=getUniqueObservations(targetName,radius_arcsec=coneradius_arcsec,columns=["obs_collection","project"])
        obspertarget.extend(uniqueObs)
        #print(k2id, uniqueObs)
        if ('HST-HST' or 'HLA-HLA') in uniqueObs:
            missing.extend([kid])
            print(uniqueObs)

    print(missing)
    names,counts=np.unique(obspertarget,return_counts=True)
    
    plt.figure(figsize=(14,7))
    plotUniqueCounts(names,counts)
    plt.title('Heartbeat stars with data from another mission, within 8 arcsec')

    return obspertarget,names,counts
    #datatypes=[]

    #    #Cone Search that epicid
    ##    targetName="EPIC %u" % np.int(k2id)
    #    mastData=api.targetNameConeSearch(targetName, radius_arcsec)
    #    data=p.DataFrame.from_dict(mastData['data'])
        
    #    uniqueprojects=data[histfield].unique()
    #    datatypes.extend(uniqueprojects)
    
    #count the number of each type.

#    names,counts=np.unique(datatypes,return_counts=True)
#
#    print(names)
#    print(counts)

if __name__ == "__main__":
    main()
