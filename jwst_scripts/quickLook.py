#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 11:46:50 2018

@author: smullally
"""

from astropy.io import fits
import getopt
import sys
import numpy as np

def main():
    
    """
    Given an input file
    return the specified header information
    -e, --ext, picks the etension to print
    -k, --key, allows you to pick a specific header keyword.
    -h, --help, help message
    """
    
    ext=0
    keyword=""
    fitsfile=""

    try:
      
        options,arg = getopt.getopt(sys.argv[1:],'hk:e:f:',['help','key=','ext=','file='])
        
    except:
        
        print("Input Arguments cannot be read")
        sys.exit("Input Arguments are incorrect.\n")
    

    
    for opt, arg in options:
        if opt in ('-h','--help'):
            print("\nI need to write a help message here. --key, --ext")
            sys.exit("\n")
        if opt in ('-k','--key'):
            keyword=arg

        if opt in ('-e','--ext'):
            ext=np.int(arg)
        if opt in ('-f','--file'):
            fitsfile=arg
            
#Read in file
    try:
        hdu=fits.open(fitsfile)
    except:
        print("\nCannot open file %s" % fitsfile)
        sys.exit("Exiting..")
        
    if (keyword==""):
        hdu.info()
        print("---\n---\n")
        print(hdu[ext].header)
    else:
        try:
            value=hdu[ext].header[keyword]
            comment=hdu[ext].header.comments[keyword]
            print(" %9s = %15s   # %s" % (keyword,value,comment))
        except (KeyError,NameError):
            sys.exit("\nERROR:  Cannot find Key %s in Extension %u" % (keyword,ext))
        
    
    
    

datadir='/Users/smullally/data/jwst/'
datadir='/Users/smullally/data/jwst/MAST_2018-04-24T1727/JWST/V80600057001P0000000002101/'

filename='jw80600057001_02101_00001_mirimage_rateints.fits'

pheader=fits.open(datadir+filename)

pheader[0].header



if __name__=="__main__":
    main()