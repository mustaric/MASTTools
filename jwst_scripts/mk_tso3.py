import numpy as np
import astropy.io.fits as fits
# Import the following to fetch dev$pix
#from pyraf import iraf

'''Build a dummy time-series image from IRAF dev$pix.
    Time offset is represented on image axis 3.
    Time at start is 2018-02-14T17:00:00
    MJD at start: 58163.70833333
    MJD at mid-point of first frame: 58163.70839120
    MJD conversion: 
        https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/xTime/xTime.pl
    Photon counting time per frame is 10.00 s
    Dead time is 0.1 s between frames
'''

wcskw3 = {
        'WCSAXES': 4,
        'RADESYS': 'ICRS',
        'CRPIX1': 257.75,
        'CRVAL1': 201.94541667302,
        'CDELT1': -2.1277777E-4,
        'CTYPE1': 'RA---TAN',
        'PC1_1':  1.,
        'PC1_2':  0.,
        'PC1_3':  0.,
        'CRPIX2': 258.93,
        'CRVAL2': 47.45444,
        'CDELT2': 2.1277777E-4,
        'CTYPE2': 'DEC--TAN',
        'PC2_1':  0.,
        'PC2_2':  1.,
        'PC2_3':  0.,
        'CRPIX3': 1.,
        'CRVAL3': 5.0,
        'CDELT3': 10.1,
        'CTYPE3': 'UTC',
        'CUNIT4': 's',
        'PC3_1':  0.,
        'PC3_2':  0.,
        'PC3_3':  1.,
        'TIMESYS': 'UTC',
        'TREFPOS': 'TOPOCENTER',
        'MJDREF': 58163.70833333,
        'MJD-BEG': 58163.70833333,
        'MJD-AVG': 58163.70839699,
        'NINTS': 10,
        'NGROUPS': 1,
        'EFFINTTM': 10.,
        'XPOSURE': 100.,
        'TELAPSE': 101.
        }

phdu_kw = {
        'TELESCOP': 'JWST',
        'DATE-OBS': '2018-01-18T17:00:00.000',
        'INSTRUME': 'NIRCAM',
        'DETECTOR': 'NRCA1',
        'MODULE': 'A',
        'CHANNEL': 'SHORT',
        'FILTER': 'F212N',
        'PUPIL': 'CLEAR',
        'TIMESYS': 'UTC',
        'TREFPOS': 'TOPOCENTER'
        }

#iraf.imcopy('dev$wpix', './wpix.fits')
with fits.open('wpix.fits') as hdu:
    pix = hdu[0].data
    hdr = hdu[0].header

arr = np.zeros((10,512,512))
for i in range(10):
    arr[i,:,:] = pix * (10.-i)/10.

phdu = fits.PrimaryHDU()
phdu.header.update(phdu_kw)

hdu3d = fits.ImageHDU(arr)
hdu3d.header.update(wcskw3)

hduList = fits.HDUList([phdu, hdu3d])
hduList.writeto('tso3_test.fits')
