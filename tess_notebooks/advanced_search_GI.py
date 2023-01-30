#%% markdown
"""
<a id="intro_ID"></a>
# Intermediate:  Search and Download GI Program Light Curves

## Introduction
This notebook uses the MAST Portal's advanced search options to retrieve the light curves for a single guest investigator program.  The notbook will show how to do an advanced query on the MAST's database of holdings, determine which data files are associated with those observations and then download the files of interest.  

For more information about the TESS mission and collected data, visit the [MAST's TESS homepage](http://archive.stsci.edu/tess/). To read more details about TESS Data Products, look in the [TESS Science Product Description Document](https://archive.stsci.edu/missions/tess/doc/EXP-TESS-ARC-ICD-TM-0014.pdf). A list of Guest Investigator programs can be found at the [TESS GI List of Approved Programs](https://heasarc.gsfc.nasa.gov/docs/tess/approved-programs.html).

### Table of Contents 
<br> [Query MAST](#query_mast)  <br> [Retrieve Product List](#product_list) <br> [Download Data](#download) <br> [Summarize Code](#summary) <br> [About this Notebook](#about_id)"""
#%% markdown
"""
***"""
#%% markdown
"""
<a id="imports_ID"></a>
## Imports
- *Observations* module from astroquery.mast is needed to make the query and download.
- *astropy.io fits* module is needed to view the downloaded fits file. 
<p>
For information on how to install astroquery see their [instructions](https://astroquery.readthedocs.io/en/latest/index.html). At the time of writing this requires the latest version on pip."""
#%% code
from astroquery.mast import Observations
from astropy.io import fits
#%% markdown
"""
<a id="query_mast"></a>
## Query the MAST CAOM Database

We want to retrieve TESS timeseries data (lightcurve and target pixel files) for the Guest Investigator program G011183 from Sector 1 (PI: Stephen Kane). We will need to query the MAST holdings database for the observations.  First we will simply count the number of observations and then we will request a table of those observations. 

All the filter names are listed on the [MAST CAOM Field Description Page](https://mast.stsci.edu/api/v0/_c_a_o_mfields.html). Or, can be found by hovering over the column names after doing a search in the MAST portal. 

The filters we will need to use are, 
- **obs_collection** to specify that we want TESS data
- **dataproduct_type** to specify that we want timeseries data
- **sequence_number** to specify that we want sector 1
- **proopsal_id** to specify the GI program number.  

Remember that more than one GI can propose for the same target so we need wild cards around the name of the program in our query."""
#%% code
obsCount = Observations.query_criteria_count(obs_collection = "TESS",\
                                       dataproduct_type = ["timeseries"],\
                                           sequence_number = 1,\
                                          proposal_id = "*G011183*")
print("Number of Observations: %i" % obsCount)#%% code
obsTable = Observations.query_criteria(obs_collection = "TESS",\
                                       dataproduct_type = ["timeseries"],\
                                           sequence_number = 1,\
                                          proposal_id = "*G011183*")
obsTable[0:5]['obsid','proposal_id','obs_id']
#%% markdown
"""
<a id="product_list"></a>
## Retrieve the list of Data Products

Next we use astroquery to retrieve the list of data products that are associated with each observation.  

We will only ask for the data products associated with the first two.  The [0:2] can be removed from the code below to get all the observations."""
#%% code
dataProducts = Observations.get_product_list(obsTable[0:2])
dataProducts.columns#%% code
dataProducts['obsID', 'productFilename', 'description']#%% markdown
"""
## Download Light curves
<a id="download"></a>
We limit our list of data products to just those with the **description** set to "Light curves" because we just want this type of data file. We then download those products and print out the manifest to show the download location. Finally we use fits.info to show the structure of the fits file. """
#%% code
want = dataProducts['description'] == "Light curves"
print(dataProducts[want])
manifest = Observations.download_products(dataProducts[want])#%% code
print(manifest)#%% code
fits.info(manifest[0])#%% markdown
"""
## Summarize Code
<a id="summary"></a>
Here is a summary of the code required to do the problem described above, without all the outputs and investigations getting in the way.  The query information is brought to the top so that it can easily be changed. For instance you might want to do a create a query on a different GI program number. """
#%% code
#Query Information
mission = "TESS"
dataProdType = ["timeseries"]
GI_program = "*G011183"
file_type = "Light curves"
sector = 1

#Query Mast Holdings
obsTable = Observations.query_criteria(obs_collection = mission,\
                                       dataproduct_type = dataProdType,\
                                           sequence_number = sector,\
                                          proposal_id = GI_program)

#Get Product List
dataProducts = Observations.get_product_list(obsTable[0:2])
want = dataProducts['description'] == file_type

#Download Data
manifest = Observations.download_products(dataProducts[want])
fits.info(manifest[0])#%% markdown
"""
***"""
#%% markdown
"""
<a id="about_id"></a>
## About this Notebook
**Author:** Susan E. Mullally, STScI Archive Scientist
<br>**Updated On:** 2018-11-29"""
#%% markdown
"""
***"""
#%% markdown
"""
[Top of Page](#title_ID)
<img style="float: right;" src="./stsci_pri_combo_mark_horizonal_white_bkgd.png" alt="stsci_pri_combo_mark_horizonal_white_bkgd" width="200px"/> """
