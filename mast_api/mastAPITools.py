#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 09:55:18 2017

@author: smullally
"""

import sys
import os
import errno
import time
import re
import json
import pandas as p

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

def mastQuery(request):
    """Perform a MAST query.
    
        Parameters
        ----------
        request (dictionary): The Mashup request json object
        
        Returns head,content where head is the response HTTP headers, and content is the returned data"""
    
    server='mast.stsci.edu'

    # Grab Python Version 
    version = ".".join(map(str, sys.version_info[:3]))

    # Create Http Header Variables
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "User-agent":"python-requests/"+version}

    # Encoding the request as a json string
    requestString = json.dumps(request)
    #pp.pprint(requestString)
    requestString = urlencode(requestString)
    # opening the https connection
    conn = httplib.HTTPSConnection(server)

    # Making the query
    conn.request("POST", "/api/v0/invoke", "request="+requestString, headers)

    # Getting the response
    resp = conn.getresponse()
    head = resp.getheaders()
    content = resp.read().decode('utf-8')

    # Close the https connection
    conn.close()

    return head,content

def retrieveMastData(uris,localFilenames,localDir="/",getNewOnly=True):
    """Ask Mast for the data once the arreay of URIs is known.
       if getNewOnly==True, It looks to see if the data is already downloaded.
       localFilename should include the full path of where it should end up
       on the local disk.
       Can handle both https:// and mast: uris.
    """
    
    try:
        os.makedirs(localDir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for i,address in enumerate(uris):
        if os.path.isfile(localDir+localFilenames[i]) & (getNewOnly):
            #print("File already exists")
            pass
        else:
            if "http" in address:
                urlretrieve(address,filename=localDir+localFilenames[i])
            else:
                server='mast.stsci.edu'
                uri = address.lstrip('mast:') # need to remove the mast: before sending to download service
                conn = httplib.HTTPSConnection(server)
                conn.request("GET", "/api/v0/download/file/"+uri)
                resp = conn.getresponse()
                fileContent = resp.read()
                with open(localDir+localFilenames[i],'wb') as FLE:
                    FLE.write(fileContent)
                conn.close()


def filterKeplerTimeseries(kepid,cadence):
    """
    Ask for either "lc" or "sc" Kepler data through a Mast.Caom.Filtered request
    Return the obsid for the observation you want.
    If returns more than 1 observations it raises an error.
    """
    cad=cadence.lower()
    
    requestFilters = [
                         {"paramName":"filters",
                          "values":["KEPLER"],
                          "separator":";"
                         },
                         {"paramName":"obs_id",
                          "values":[],
                          "freeText":"%"+cad+"%"},
                        #  },
                          {"paramName":"target_name",
                           "values":[],
                           "freeText":"%"+kepid+"%"}
                     ]

    
    mashupRequest = {"service":"Mast.Caom.Filtered",
                     "format":"json",
                     "params":{
                         "columns":"COUNT_BIG(*)",
                         "filters":requestFilters
                         }}
    
    headers,outString = mastQuery(mashupRequest)
    countData = json.loads(outString)
    numObs=countData['data'][0]['Column1']
    if numObs == 1:
            #If only one observations, request the obsID
            mashupRequest = {"service":"Mast.Caom.Filtered",
                           "format":"json",
                           "params":{
                           "columns":"*",
                           "filters":requestFilters
                         }}
         
            headers,outString = mastQuery(mashupRequest)  
            obsProducts=json.loads(outString)
            obsid=obsProducts["data"][0]["obsid"]
    else:
        raise ValueError("Number of Observations found in Filtered Query is not equal to 1")
    
    return obsid
   
    

def downloadKeplerTimeseries(kepid,cadence,localDir,getNewOnly=True):
    """
    Download the Kepler timeseries data. 
    Kepid is an integer.
    cadence is one of "lc", "sc", or "dv" (last is for dv time series)
    localDir is the directory to which the data will be written.
    getNewOnly=False will dowload the data whether it exists or not.
    Counts the files before retrieving them. If count is > 100, it raises an error.
    
    """  
    kepid_str="%09u" % kepid
    cad=cadence.lower()
    if cad == 'dv':
        getcad='lc'
        ext='_dv'  #Gets the reprots as well as the time series
    elif cad == 'lc':
        getcad=cad
        ext='llc'
    elif cad == 'sc':
        getcad=cad
        ext='slc'
        
    obsid=filterKeplerTimeseries(kepid_str,getcad)
    
    productRequest = {'service':'Mast.Caom.Products',
                 'params':{'obsid':obsid},
                 'format':'json',
                 'pagesize':100,
                 'page':1}   

    headers,obsProductsString = mastQuery(productRequest)
    
    obsProducts = json.loads(obsProductsString)
    
    #print("Number of data products:",len(obsProducts["data"]))
    
    dfProd = p.DataFrame.from_dict(obsProducts["data"])
    wantprod=(dfProd['productFilename'].str.contains(ext))
    #wantdv=(dfProd['description'].str.contains('Data Validation'))
    #want=wantprod | wantdv
    
    #Get the URLS
    uris=np.array(dfProd[wantprod]['dataURI'])
    filenames=np.array(dfProd[wantprod]['productFilename'])

    #Direct Download of Data,  
    
    retrieveMastData(uris,filenames,localDir=localDir+kepid_str+'/',getNewOnly=getNewOnly)
    
def targetNameConeSearch(targetName, radius_arcsec, pagesize=2000,npages=1):
    """
    Do a cone search for products around a given target name.
    targetName is a string
    radius_arcsec is the radius of the cone search.
    """


    resolverRequest = {'service':'Mast.Name.Lookup',
                         'params':{'input':targetName,
                                   'format':'json'},
                         }
    
    headers,resolvedObjectString = mastQuery(resolverRequest)
    
    resolvedObject = json.loads(resolvedObjectString)
    #print("Information about KIC Object")
    #pp.pprint(resolvedObject)
    try:
        objRa = resolvedObject['resolvedCoordinate'][0]['ra']
        objDec = resolvedObject['resolvedCoordinate'][0]['decl']
    
        #Ask for data products within a cone search of that RA and Dec
        #Mast wants radius in arc minutes
        
        mastRequest = {'service':'Mast.Caom.Cone',
                       'params':{'ra':objRa,
                                 'dec':objDec,
                                 'radius':radius_arcsec/3600},
                       'format':'json',
                       'pagesize':pagesize,
                       'page':npages,
                       'removenullcolumns':True,
                       'removecache':True}
        
        headers,mastDataString = mastQuery(mastRequest)
        
        mastData = json.loads(mastDataString)
    except IndexError:
        mastData=dict()
        mastData['data']=[]
        print('oops no data')
        print(targetName)
    
    return mastData
    
def coneSearchWithProjectCounts(ra,dec,radius_arcmin,project,maxData=1000000):
    """
    Do a cone search, but only return those from a particular project.
    """
    posreq= "%f, %f, %f" % (ra,dec,radius_arcmin)
    
    mashupRequest = {
             "service":"Mast.Caom.Filtered.Position",
             "format":"json",
             "params":{
                 "columns":"COUNT_BIG(*)",
                 "filters":[
                     {"paramName":"project",
                      "values": project
                    }],
                "position":posreq
            }}
    
    print(mashupRequest)
    headers,outString = mastQuery(mashupRequest)
    outData = json.loads(outString)
    print(outData)
    numObs=outData['data'][0]['Column1']
    print(numObs)
    
    if numObs < maxData:
        mashupRequest = {
            "service":"Mast.Caom.Filtered.Position",
            "format":"json",
            "params":{
              "columns":"*",
              "filters":[
                    {"paramName":"project",
                     "values": project
                     }],
               "position":posreq
            }}
        headers,outString = mastQuery(mashupRequest)
        outData = json.loads(outString)
    
        
        return outData