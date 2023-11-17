#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 11:26:04 2023

@author: smullally
"""

"""
This code is to show a plot of IP addresses per country.

It uses geopandas to create a world map.

If you have counts per country code, this will draw a map 
It uses geopandas for the map
and pycountry to convert the country codees.


"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas
import pycountry
import geoplot
import mapclassify
import pypopulation


def get_a3_codes_from_a2(df, col_name = 'a2'):
    
    a3list = []
    
    for i, a2name in enumerate(df[col_name]):
        
        try:
            country = pycountry.countries.get(alpha_2=a2name)
            a3list.append(country.alpha_3)
            
        except AttributeError:
            print(a2name)
            if a2name == "XK":
                a3list.append("XKK")  #Kosovo
            else:
                a3list.append(" ")
        except LookupError:
             print(a2name)
             if a2name == "XK":
                a3list.append("XKK")  #Kosovo
             else:
                a3list.append(" ")
            
    return a3list


def plot_world(stats, zcol="", title="Countries that Request MAST Data.", 
               bins =  (1, 100, 300, 1000,3000)):
    
    ax = geoplot.polyplot(stats, projection=geoplot.crs.Robinson(), figsize=(8, 4))
    ax.outline_patch.set_visible(True)
    scheme = mapclassify.UserDefined(stats[zcol], bins ,lowest=0)

    ax = geoplot.choropleth(
        stats, hue=stats[zcol], scheme=scheme,
        cmap='Greens', figsize=(15, 8), legend=True, 
        edgecolor='black', legend_kwargs={'loc':"lower center"},
        projection=geoplot.crs.Robinson()
    )
    
    handles, labels = ax.get_legend_handles_labels()
    ax.set_facecolor('lightblue')
    plt.title(title)


#%%
#-----------------
datapath = "/Users/smullally/Python_Code/MASTTools/geoloc/mast_geoloc/requests_mast_last90days.csv"

ipcounts = pd.read_csv(datapath)

path = geopandas.datasets.get_path('naturalearth_lowres')
geodf = geopandas.read_file(path)
geodf.at[43,'iso_a3'] = 'FRA'
geodf.at[21,'iso_a3'] = 'NOR'
geodf.at[174,'iso_a3'] = 'XKK'
#geodf.at[41, 'iso_a3'] = 'GUY'
#geodf.at[42, 'iso_a3'] = 'SUR'

a3codes = get_a3_codes_from_a2(ipcounts, col_name = "iso_code")
ipcounts['alpha_3'] = a3codes

#Need to merge the ipcounts and the a3codes together with the geodf to get geometry
stats = geodf.copy()

stats = stats.merge(ipcounts, how='left', right_on='alpha_3', left_on='iso_a3',suffixes=['','mast'])
stats['Unique IP Addresses'] = stats['Unique IP Addresses'].fillna(0)
stats['Total Requests'] = stats['Total Requests'].fillna(0)
#stats = stats.merge(portal,how='left', right_on='alpha_3', left_on='iso_a3',suffixes=['','portal'])
#stats['Sum of download.size'] = stats['Sum of download.size'].fillna(0)


plot_world(stats, zcol="Unique IP Addresses", title="Unique IP Addresses by Country \n(Nov 2022-Jan 2023)")
plt.savefig("/Users/smullally/Python_Code/MASTTools/geoloc/mast_geoloc/uniqueip_mast_nov2022-jan2023.png")

#%%
plot_world(stats, zcol="Total Requests", title="Total Requests by Country \n(Nov 2022-Jan 2023)",
           bins = (0,10,100,1000,10000,1e6,1e9))
plt.savefig("/Users/smullally/Python_Code/MASTTools/geoloc/mast_geoloc/totalrequest_mast_nov2022-jan2023.png")

