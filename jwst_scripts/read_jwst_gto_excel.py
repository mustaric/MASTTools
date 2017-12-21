#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:30:57 2017

@author: smullally
"""

#This is code to read in the JWST excel spreadsheet so we can do useful things
#like compare them to the output of the portal when that is up and running

import pandas as p
import numpy as np

from astropy import units as u
from astropy.coordinates import SkyCoord


def convertSkyCoords(ra,dec,ret='ra'):
    """Given ra/dec in hexadecimal, convert to degrees
    Needs to be robust against erroneous text in the ra dex fields
    Need to check if they are already in degrees (skycoord already does this)
    In those cases of erroneous text return values of 0,0
    """
    try:
        coord=SkyCoord(ra,dec,frame='icrs',unit=(u.deg,u.deg))
        
    except (ValueError,TypeError):
        coord=SkyCoord(0,0,frame='icrs',unit=(u.deg,u.deg))
        
    if ret=='ra':
        value=coord.ra.deg
    elif ret=='dec':
        value=coord.dec.deg
    else:
        value=np.nan
    
    return value

def checkInstrumentName(name):
    
    
    try:
        checkname=name.strip().lower()
    except AttributeError:
        checkname='Other'
        
    if checkname=='miri':
        newname='MIRI'
    elif checkname=='nircam':
        newname='NIRCam'
    elif checkname=='nirspec':
        newname='NIRSpec'
    elif checkname=='niriss':
         newname='NIRISS'
    else:
        newname=checkname
    
    return newname

def getObsSheet(filename,sheetname):
    """
    Get the datafrme for the JWST observation sheet specified.
    """
    
    if sheetname=='MIRI':
        colNames=['pi','obsnum','obsid','instrument','mode','target','ra_hex','dec_hex',\
          'subarray','timeCritical','t1','t2','phase','too','disToo',\
          'coordParallel','prime','assoc','filter','channel','mask','totPhoton']
        useCol=None
    elif sheetname=='NIRISS':
        colNames=['pi','obsnum','obsid','instrument','mode','target','ra_hex','dec_hex',\
          'subarray','timeCritical','t1','t2','phase','too','disToo',\
          'coordParallel','prime','assoc','filter','pupil','totPhoton']
        useCol=None 
    elif sheetname=='NIRCam':
        colNames=['pi','obsnum','obsid','instrument','mode','target','ra_hex','dec_hex',\
          'subarray','timeCritical','t1','t2','phase','too','disToo',\
          'coordParallel','prime','assoc','filter','pupil',\
          'filter','pupil','filter','pupil','filter','pupil','mask','totPhoton']
        useCol=None
    elif sheetname=="NIRSpec MOS":
        useCol=np.arange(0,13,1)
        colNames=['pi','obsnum','obsid','instrument','mode','ra_hex','dec_hex',\
          'timeCritical','t1','t2','phase','too','disToo']
    elif sheetname=="NIRSpec FSS & IFU":
        useCol=np.arange(0,15,1)
        colNames=['pi','obsnum','obsid','instrument','mode','target','ra_hex','dec_hex',\
                  'subarray','timeCritical','t1','t2','phase','too','disToo']        
        
    print(colNames)
    print(sheetname)
    #Note that rows 2 and 3 in the excell spreadsheet are one, 
    #so need to only skip 2 rows
    df=p.read_excel(filename,sheetname,skiprows=[0,1],\
                    names=colNames,usecols=useCol)


    ras_deg = list(map(lambda r,d :convertSkyCoords(r,d,ret='ra'), \
                       df.ra_hex,df.dec_hex))
    decs_deg = list(map(lambda r,d :convertSkyCoords(r,d,ret='dec'), \
                        df.ra_hex,df.dec_hex))

    newinstrument = list(map(lambda name : checkInstrumentName(name), df.instrument))
    
    df['instrument']=newinstrument
    df['ra_deg']=ras_deg
    df['dec_deg']=decs_deg
    
    #Drop empty rows, those with now obsid
    v=df[df.obsid.isnull()].index
    print(v)
    df.drop(v,inplace=True)

    
    return df


def main():
    
    """For a JWST Observation Specification all file in excel
    read in and send back all the sheets in their own data frame.
    """
    obsFilename='/Users/smullally/JWSTops/plannedObservations/JWST_GTO_Observation_Specifications_all.xlsx'

    xls=p.ExcelFile(obsFilename)

    print(xls.sheet_names)
    miri=getObsSheet(obsFilename,'MIRI')
    
    niriss=getObsSheet(obsFilename,'NIRISS')
    
    nircam=getObsSheet(obsFilename,'NIRCam')
    
    nirspecmos=getObsSheet(obsFilename,'NIRSpec MOS')
    
    nirspecfss=getObsSheet(obsFilename,'NIRSpec FSS & IFU')
    
    alldf= [miri,niriss,nircam,nirspecmos,nirspecfss]
    
    allObs=p.concat(alldf,axis=0,join='inner')
    
    return allObs