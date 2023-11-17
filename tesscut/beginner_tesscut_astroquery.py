#%% markdown
"""
<a id="title_ID"></a>
# Beginner: Cutout of the TESS FFIs using Astrocut and Astroquery

This notebook shows the user how to use the MAST programmatic interface to create a cutout of the small section of the TESS FFIs. For this example we will determine the RA and Dec for TIC 261105201. We then perform a query to determine which sectors contain this RA and Dec, peform a cutout of the FFI time series, open the resulting target pixel files, and plot the first image of each file with the WCS overlayed on the image. Finally we will create a light curve from the resulting image by creating a photometric aperture and summing the light in our pixels.  

This tutorial shows the users how to do the following: use astroquery.catalogs to query the TIC, use astroquery Tesscut to determine the number of sectors that contain our target and download a FFI cutout.


### Table of Contents 
  [Astroquery Search of the TIC](#catalog_ID) <br> 
  [Tesscut to Perform FFI Cutout](#tesscut_ID) <br>
  [Create Light Curve](#lightcurve) <br>
  [Additional Resources](#resources_ID) <br> 
  [About this Notebook](#about_ID) 
"""
#%% markdown
"""
***
"""
#%% markdown
"""
## Import Statements
<a id="imports_ID"></a>

We start with a few import statements.
- *numpy* to handle array functions
- *astropy.io fits* for accessing FITS files
- *astropy.wcs WCS* to interpret the World Coordinate Systems
- *matplotlib.pyplot* for plotting the data
- *astroquery.mast* for the catalogs and for tesscut.

For ease of use later on, we also set the root url for the Tesscut package here.

If your version of astroquery doesn't have tesscut, try
pip install astroquery==0.3.9.dev5086
"""
#%% code
import numpy as np
from astroquery.mast import Catalogs
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.io import fits
import matplotlib.pyplot as plt

#%matplotlib inline

###CHANGE THE NEXT LINE in Pull Request ###
#This is the url we are using.
Tesscut._TESSCUT_URL = 'https://mast.stsci.edu/tesscut/api/v0.1/'
#%% code
# DELETE THIS CELL

#Next line puts your mast api token in a useful variable for later.
#See https://auth.mast.stsci.edu/info
#masttoken = %env MAST_DV_TOKEN
#Tesscut._session.headers["Authorization"] = "token %s" % "2a1f8c7e0e924cbaaa256b296ed80ce0"
#%% markdown
"""
***
"""
#%% markdown
"""
<a id="catalog_ID"></a>
## Get Coordinates of the Target Using Astroquery Catalogs

Here we use the astroquery.mast Catalogs query_criteria function to request the RA and Dec of the object with TIC ID = 261105201.   
<p>
Here we do a cone search using Catalogs.query_object on the TIC catalog. The advantage of doing this (instead of a directly criteria query on the Tess Input Catalog) is that it gives us the nearby stars as well as the star we are looking for. The resulting table is sorted by distance from the requested object. We print out the ID and a few other TIC quantities to ensure we found the star we were looking for. 
"""
#%% code
ticid = 261105201

starName = "TIC " + str(ticid)
rad_search = 4/60 #radius in degrees

catalogData = Catalogs.query_object(starName, radius = rad_search, catalog = "TIC")
Ra = catalogData[0]['ra']
Dec = catalogData[0]['dec']

#Print out the first row in the table
print( catalogData[:5]['ID', 'Tmag', 'Jmag', 'ra', 'dec', 'objType'] )
#%% code
# Create a list of nearby bright stars (tess magnitude less than 14) from the rest of the data for later.
bright = catalogData['Tmag'] < 15

# Make it a list of Ra, Dec pairs of the bright ones. This is now a list of nearby bright stars.
nearby_stars = list( map( lambda x,y:[x,y], catalogData[bright]['ra'], catalogData[bright]['dec'] ) )
len(nearby_stars)
#%% markdown
"""
***
"""
#%% markdown
"""
## Query Which Sectors are Available
<a id="catalog_ID"></a>
Using the TESS sector information service, we make a request to determine which sectors/cameras/CCDs contain data for this target. Remember that there is a set of FFIs for each TESS sector and those are broken up into 4 cameras which each have 4 CCDs.  We will do this with a radius=0 cone search to find only those FFI sets that contain the star of interest. You can also make the query using a larger radius, which may be important if the star is near the edge of one of the CCDs.
<p>
Note, the request is returned in a json format. The 'results' key contains an array of dictionaries with the information we are looking for.  
"""
#%% code
coord = SkyCoord(Ra, Dec, unit = "deg")

sector_table = Tesscut.get_sectors(coord)
print(sector_table)
#%% markdown
"""
The resulting table shows that this target was observed in two different sectors using the same camera and CCD.
"""
#%% markdown
"""
***
"""
#%% markdown
"""
<a id="tesscut_ID"></a>
## Request pixel timeseries cutout from TESS FFIs
Astrocut is the tool that runs the cutout service around the RA and Dec that were requested. It delivers a zipped file containing a cutout for each set of FFIs as listed above. It is also possible to request only one sector using the "sector" parameter.  
<br>
For tesscut, ***x*** refers to the CCD columns and ***y*** refers to the CCD rows. Distance can be input in a variety of units, I chose pixels ("px").
"""
#%% code
hdulist = Tesscut.get_cutouts(coord, 20)
#%% markdown
"""
Notice that this returns a **list** of HDUlist objects, one for each of our files.  HDUlist objects are the same thing you get back as if you downloaded the file and then run the following on the file: 
hdu =  astropy.io.fits.open(FITS_file_name)
"""
#%% code
hdulist[0].info()
hdulist[0][0].header['SECTOR']
#%% code
hdulist[1].info()
#%% markdown
"""
[Top of Page](#title_ID)
"""
#%% markdown
"""
***
"""
#%% markdown
"""
<a id="plot_image"></a>
## Plot the First Image of the Time Series
Here we show you some of the information found in the cutout. The format is almost identical to a target pixel file. You might read through the target pixel file tutorial if you are not familiar with that file type.  

The pixel-level data is stored in the first PIXELS extension, including an array of the calibrated pixels for each time stamp. See the column called 'FLUX'. 

"""
#%% code
# Define a function to simplify the plotting command that we do repeatedly.
def plot_cutout(image):
    """
    Plot image and add grid lines.
    """
    plt.imshow(image, origin = 'lower', cmap = plt.cm.YlGnBu_r, 
           vmax = np.percentile(first_image, 92),
           vmin = np.percentile(first_image, 5))

    plt.grid(axis = 'both',color = 'white', ls = 'solid')
#%% code
hdu1 = hdulist[0]
first_image = hdu1[1].data['FLUX'][0]

fig = plt.figure(figsize=(7, 7))
plot_cutout(first_image)
plt.xlabel('Image Column',fontsize = 14)
plt.ylabel('Image Row',fontsize = 14)
#%% markdown
"""
### Show the first image of the second file 
We also add a WCS to the image and mark the requested star as well as nearby stars.
We use the WCS in the header to place a red dot on the image for the catalog position of the star on the figure as a demonstration of the WCS. The orange dots are the nearby stars found in the cone search done above. 

**Note. The WCS is based on the WCS stored in the FFI file for the central part of the time series and there can be some motion during a sector of observation.**
"""
#%% code
hdu2 = hdulist[1]

first_image = hdu2[1].data['FLUX'][0]

wcs = WCS(hdu2[2].header)

fig = plt.figure(figsize = (8, 8))
fig.add_subplot(111, projection = wcs)
plot_cutout(first_image)

plt.xlabel('RA', fontsize = 12)
plt.ylabel('Dec', fontsize = 12)


starloc = wcs.all_world2pix([[Ra,Dec]],0)  #Second is origin
plt.scatter(starloc[0,0], starloc[0,1],s = 45,color = 'red')

# Plot nearby stars as well, which we created using our Catalog call above.
nearbyloc = wcs.all_world2pix(nearby_stars[1:],0)
plt.scatter(nearbyloc[1:, 0], nearbyloc[1:, 1], 
            s = 25, color = 'orange')
#%% markdown
"""
<a id="lightcurve"></a>
## Create a Light Curve from the Cutout

We create two functions.  One to appply a phtometric aperture to one image and the other to then apply that to all the images in the FLUX array.
"""
#%% code
def aperture_phot(image, aperture):
    """
    Sum-up the pixels that are in the aperture for one image.
    image and aperture are 2D arrays that need to be the same size.
    
    aperture is a boolean array where True means to include the light of those pixels.
    """
    flux = np.sum(image[aperture])

    return flux

def make_lc(flux_data, aperture):
    """
    Apply the 2d aperture array to the and time series of 2D images. 
    Return the photometric series by summing over the pixels that are in the aperture.
    
    Aperture is a boolean array where True means it is in the desired aperture.
    """
    
    flux = np.array(list (map (lambda x: aperture_phot(x, aperture), flux_data) ) )

    return flux
#%% markdown
"""
### Create a photometric time series using all the pixels in the image.
The third extension indicates which pixels have data in your image. To use all the returned pixels, we set our 2D aperture array to be True for all those with a value of 1 in that image. 
"""
#%% code
#Use all pixels in our aperture.
aperture = hdu1[2].data == 1

flux1 = make_lc(hdu1[1].data['FLUX'],aperture)
time1 = hdu1[1].data['TIME']

plt.figure(figsize = (11,5))
plt.plot(time1, flux1, 'k.-', lw = .5)
plt.xlim(1325,1342)
plt.xlabel('TIME (BTJD)')
plt.ylabel('Flux (e-/s)')
plt.title('Flux in Photometric Aperture')
#%% markdown
"""
### Estimate the background
No background subtraction has been performed on these images.  We estimate the background by using numpy's percentile function and selecting those pixels from the first image below the 5th percentile as a way of estimating the background.
"""
#%% code
# Plot the flux change of the dimmest pixels by using percentile.
bkg_aperture = hdu1[1].data['FLUX'][0] < np.percentile(hdu1[1].data['FLUX'][0], 5)

bkg_flux1 = make_lc(hdu1[1].data['FLUX'], bkg_aperture)
time1 = hdu1[1].data['TIME']

plt.figure(figsize = (11, 5))
plt.plot(time1, bkg_flux1, 'r.-',lw = .5)

plt.xlim(1325, 1342)
plt.xlabel('TIME (BTJD)')
plt.ylabel('Estimate of Background')
plt.title('Background Flux')
#%% markdown
"""
### Subtract the background from the flux time series
Subtract this background after accounting for the number of pixels used to estimate the flux of the background relative to the entire image.  The final plot shows that the background subtraction removed much of unexpected variation.  This is likely an eclipsing binary system.  
"""
#%% code
bkgsub_flux = flux1 - (bkg_flux1 * np.sum(aperture) / np.sum(bkg_aperture) )

plt.figure(figsize = (11,5))
plt.plot(time1, bkgsub_flux,'.-k', lw = 0.5)

plt.xlim(1325, 1336)
plt.xlabel('TIME (BTJD)')
plt.ylabel('Flux (e-/s)')
plt.title('Background Subtracted Flux')
#%% markdown
"""
<a id="resources_ID"></a>
## Additional Resources
[TESScut API Documentation](https://mast.stsci.edu/tesscut/)<br>
[Astrocut Documentation](https://astrocut.readthedocs.io/en/latest/)<br>
[TESS Homepage](https://archive.stsci.edu/tess)<br>
[TESS Archive Manual](https://outerspace.stsci.edu/display/TESS/TESS+Archive+Manual)

"""
#%% markdown
"""
***
"""
#%% markdown
"""
<a id="about_ID"></a>
## About this Notebook
**Author:** Susan E. Mullally, STScI Archive Scientist
<br>**Updated On:** 2018-12-03
"""
#%% markdown
"""
[Top of Page](#title_ID)
<img style="float: right;" src="./stsci_pri_combo_mark_horizonal_white_bkgd.png" alt="stsci_pri_combo_mark_horizonal_white_bkgd" width="200px"/> 
"""
