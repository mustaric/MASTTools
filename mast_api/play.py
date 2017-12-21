#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 09:50:28 2017

@author: smullally
"""

import sys
import os
import time
import re
import json
import mastAPITools as api

try: # Python 3.x
    from urllib.parse import quote as urlencode
    from urllib.request import urlretrieve
except ImportError:  # Python 2.x
    from urllib import pathname2url as urlencode
    from urllib import urlretrieve

try: # Python 3.x
    import http.client as httplib 
except ImportError:  # Python 2.x
    import httplib   

from astropy.table import Table
import numpy as np

import pprint
pp = pprint.PrettyPrinter(indent=4)

import pandas as p


#%%
#I want to try to get a particular Kepler Id through the mastQuery API
#This does not require a cone search, only knowledge of the KIC ID.

kicid='011904151' #Kepler 10
#Step 0 get ra and dec for the kepler ID of interest
#Step one should be to ask if MAST has any data I want
#Step two should be to download the data (i.e. put it in the basket and retrieve)

#Step 0 -- get RA and Dec
objectOfInterest = 'KIC %s' % kicid

resolverRequest = {'service':'Mast.Name.Lookup',
                     'params':{'input':objectOfInterest,
                               'format':'json'},
                     }

headers,resolvedObjectString = api.mastQuery(resolverRequest)

resolvedObject = json.loads(resolvedObjectString)
print("Information about KIC Object")
pp.pprint(resolvedObject)

objRa = resolvedObject['resolvedCoordinate'][0]['ra']
objDec = resolvedObject['resolvedCoordinate'][0]['decl']

#Step 1
#Ask for data products within a cone search of that RA and Dec
coneradius_arcsec = 5

mastRequest = {'service':'Mast.Caom.Cone',
               'params':{'ra':objRa,
                         'dec':objDec,
                         'radius':coneradius_arcsec/60},
               'format':'json',
               'pagesize':2000,
               'page':1,
               'removenullcolumns':True,
               'removecache':True}

headers,mastDataString = api.mastQuery(mastRequest)

mastData = json.loads(mastDataString)

pp.pprint(mastData['fields'][:25])

#Limit that search to Kepler data with the original object ID.
#%%
#Limit that data to those with the right target_name and instrument_name

print(mastData.keys())
print("Query status:",mastData['status'])

#Convert the data to pandas dataframe

dfData=p.DataFrame.from_dict(mastData['data'])
print(dfData[:3])

#Create a dataframe of just those I want

wantdata=(dfData['target_name'] == 'kplr' + kicid) & (dfData['instrument_name']=='Kepler')
lcwant=(dfData['t_exptime'] == 1800)
scwant=(dfData['t_exptime'] == 60)

getdata=dfData[wantdata & lcwant]
obsid = np.int(dfData[wantdata & lcwant]['obsid'])

#Request The Products for this observation

productRequest = {'service':'Mast.Caom.Products',
                 'params':{'obsid':obsid},
                 'format':'json',
                 'pagesize':100,
                 'page':1}   

headers,obsProductsString = api.mastQuery(productRequest)

obsProducts = json.loads(obsProductsString)

print("Number of data products:",len(obsProducts["data"]))
print("Product information column names:")
pp.pprint(obsProducts['fields'])

dfProd = p.DataFrame.from_dict(obsProducts["data"])
wantprod=(dfProd['description'].str.contains('CLC')) & (dfProd['description'].str.contains('Q'))
wantdv=(dfProd['description'].str.contains('Data Validation'))
want=wantprod | wantdv

#Get the URLS
uris=np.array(dfProd[want]['dataURI'])
filenames=np.array(dfProd[want]['productFilename'])

#%%
#Direct Download of Data, now done through mastAPITools.py
#Just need a list of URIs and FileNames.
getNewOnly=True #If True then won't download if the file already exists on disk
storedir="/Users/smullally/MastData/Kepler/" + kicid+'/'

api.retrieveMastData(uris,filenames,localDir=storedir,getNewOnly=True)



#%%
#Here is another way to find the data without doing a cone search.
#Mast.Caom.Filtered
#kicid=011904151

kicid='011904151'
kepid = 'kplr' + kicid
inst = 'Kepler'
exptime = 1800

#requestFilters = [{"paramName":"filters",
#                          "values":["KEPLER"]},
#                         {"paramName":"obs_collection",
#                           "values":["Kepler"]
#                         },
#                         {"paramName":"t_exptime",
#                          "values":[exptime],
#                          "separator":';'
#                         },
#                         {"paramName":"target_name",
#                          "values":[kepid]
#                         },
#                         {"paramName":"obs_id",
#                          "values":[],
#                          "freeText":"%lc%"
#                         }
#                         ]
requestFilters = [
                         {"paramName":"filters",
                          "values":["KEPLER"],
                          "separator":";"
                         },
                         {"paramName":"obs_id",
                          "values":[],
                          "freeText":"%lc%"},
                        #  },
                          {"paramName":"target_name",
                           "values":[],
                           "freeText":"%"+kicid+"%"}
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

pp.pprint(countData)


#%%
#Let's try an epic search for for K2, do a narrow cone search
#
import pandas as p
epicid=228813918
targetName="EPIC %u" % epicid
radius_arcsec = 8


mastData=api.targetNameConeSearch(targetName, radius_arcsec)

pp.pprint(mastData['data'][:25])
data=p.DataFrame.from_dict(mastData['data'])
uniqueprojects=data.project.unique()
uniquefilters=data.filters.unique()
print(uniqueprojects)
print(uniquefilters)

#%%
#Try to get a list of targets observed by Kepler spacecraft wtih 

start="2016-07-13 02:04:00"
from astropy.time import Time
times=[start]
t=Time(times,format='iso', scale='utc')
print(t)
print(t.mjd)

requestFilters = [
                         {"paramName":"project",
                          "values":["K2","Kepler"],
                          "separator":";"
                         },
                         {"paramName":"t_min",
                          "values":[{"min":t.mjd[0]-.5 , "max":t.mjd[0]+.5}]
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

pp.pprint(countData[:10])


#%%
#TIC Stuff

afilter=[{"paramName":"ID","values":["1234567"]}]

service="Mast.Catalogs.Filtered.Tic"
aformat="json"

cols="*"
request={"service":service,"format":aformat,
         "params":{"columns":cols,"filters":afilter}}

headers,outString = api.mastQuery(request)

outData=json.loads(outString)

mydata=p.DataFrame.from_dict(outData['data'])
print(mydata.ID)
print(mydata.Tmag)
