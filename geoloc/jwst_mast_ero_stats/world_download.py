#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAST Download statistics. Combining AWS and Portal stats
Using geopandas to create a world map.

Created on Sun Jul 17 15:10:18 2022

@author: smullally
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from cartopy import crs as ccrs
import pycountry

path = geopandas.datasets.get_path('naturalearth_lowres')
df = geopandas.read_file(path)
df.at[43,'iso_a3'] = 'FRA'
df.at[21,'iso_a3'] = 'NOR'

datafile = "/Users/smullally/Python_Code/jwst_project/mast_stats/ip_stats_summary_country_13-182022.csv"

aws = pd.read_csv(datafile)
aws.columns

datafile = "/Users/smullally/Python_Code/jwst_project/mast_stats/location_stats_portal_13-18.csv"

portal = pd.read_csv(datafile)
portal.columns

#%%

def get_a3_codes_from_name(df, col_name = 'country_name'):
    
    a3list = []
    
    for i,cname in enumerate(df[col_name]): 
        
        try:
            country = pycountry.countries.get(name=cname)
        
            a3name = country.alpha_3
            a3list.append(a3name)
        except AttributeError:
            try:
                country = pycountry.countries.get(common_name = cname)
                a3name = country.alpha_3
                a3list.append(a3name)
            except AttributeError:
                if cname == "Russia":
                    a3list.append('RUS')
                elif cname == "Iran":
                    a3list.append('IRN')
                elif cname == "Vatican City":
                    a3list.append('VAT') 
                else:    
                    a3list.append("")
                    print(cname)
                    


    return a3list

def get_a3_codes_from_a2(df, col_name = 'a2'):
    
    a3list = []
    
    for i, a2name in enumerate(df[col_name]):
        
        try:
            country = pycountry.countries.get(alpha_2=a2name)
            a3list.append(country.alpha_3)
            
        except AttributeError:
            print(a2name)
            a3list.append(" ")
            
    return a3list

#%%

a3list = get_a3_codes_from_name(aws,col_name = 'country_name')

aws['alpha_3'] = a3list

a3list= get_a3_codes_from_a2(portal, "geoip.country_iso_code: Descending")
portal['alpha_3'] = a3list

#%%

stats = df.copy()

stats = stats.merge(aws, how='left', right_on='alpha_3', left_on='iso_a3',suffixes=['','aws'])
stats['total_volume_terabytes'] = stats['total_volume_terabytes'].fillna(0)
stats = stats.merge(portal,how='left', right_on='alpha_3', left_on='iso_a3',suffixes=['','portal'])
stats['Sum of download.size'] = stats['Sum of download.size'].fillna(0)
len(stats)
    
total_tb = stats['Sum of download.size']*1e-12 + stats['total_volume_terabytes']

stats['Total_TB'] = total_tb

stats['Total_TB'] = stats['Total_TB'].fillna(0)
#stats['Total_TB'] = stats['Total_TB'].replace(0,-10)
#%%

#Do Some plotting

import geoplot
import mapclassify


ax = geoplot.polyplot(stats, projection=geoplot.crs.Robinson(), figsize=(8, 4))
ax.outline_patch.set_visible(True)
scheme = mapclassify.UserDefined(stats['Total_TB'], (.0001,.5,2,8,150),lowest=0)
#%%

ax = geoplot.choropleth(
    stats, hue=stats['Total_TB'], scheme=scheme,
    cmap='Greens', figsize=(15, 8), legend=True, 
    edgecolor='black', legend_kwargs={'loc':"lower center"},
    projection=geoplot.crs.Robinson()
)
handles, labels = ax.get_legend_handles_labels()
ax.set_facecolor('lightblue')
plt.title("Countries that Downloaded JWST Data by Volume 2022-07-13 -- 2022-07-18")

plt.savefig("/Users/smullally/Python_Code/jwst_project/mast_stats/world_download_5day.png") 

#%%
#Plot of AWS data by IP address
                