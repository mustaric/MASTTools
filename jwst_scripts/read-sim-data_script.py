# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
 
ddir="/grp/jwst/ssb/test_build7.1/examples_for_dms/level2/nrs_fixedslit/"
myfile=ddir + "jwtest1013001_01101_00001_NRS1_cal.fits"

ddir="/grp/jwst/dms2/testdata/TSO/NIRCam/wasp80/ins-fits/"
myfile=ddir + "NRCA1_F444W.fits"

ddir="/grp/jwst/dms2/testdata/TSO/NIRISS/GJ436/ins-fits/"
myfile=ddir+"niriss_soss_gj436_exposure_x1dints.fits"

fitsdata=fits.open(myfile,memmap=True) #Memmap=True necessary for large files

fitsdata.info()

print("Primary Header")
print(fitsdata[0].header[:40])
#%%
nhdu=4


print("HDU Header")
print(fitsdata[nhdu].header[:20])
data=fitsdata[nhdu].data
plt.figure(1,dpi=200)
plt.clf()

xtension=fitsdata[nhdu].header['XTENSION']
extname=fitsdata[nhdu].header['EXTNAME']

if fitsdata[nhdu].header['XTENSION'] == "IMAGE":
    low=np.percentile(data,1)
    high=np.percentile(data,99)
    plt.imshow(data,vmin=low,vmax=high)
    plt.title(extname)
elif fitsdata[nhdu].header['XTENSION'] == "BINTABLE":
    #"Plot column 1 vs column2"
    print(extname)
    print(data.columns)
    col1=fitsdata[nhdu].header['TTYPE1']
    col2=fitsdata[nhdu].header['TTYPE2']
    plt.plot(data[col1],data[col2],'.-',ms=3,lw=1)
    plt.xlabel(col1)
    plt.ylabel(col2)
   fit plt.title(extname)

#%%