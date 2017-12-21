#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IO code to read in Portal downloads

Created on Thu Dec 21 13:46:05 2017
IO code

@author: smullally
"""
import pandas as p
from astropy import units as u
from astropy.coordinates import SkyCoord

def readPortalJson(filename):
    """
    Read in a Portal Json formated file
    This doesn't appear to work.  --FIX--
    """
    
    df=p.read_json(filename)
    
    return df

def readPortalCsv(filename):
    """
    Read in a csv from the MAST Portal
    """
    
    df=p.read_csv(filename,sep=',',comment='#')
    
    return df


    
    