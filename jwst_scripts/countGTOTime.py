#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 11:32:31 2018

@author: smullally
"""
allObs,alldf=readgto.main()
#replace nan with zero
for df in alldf:
    df.fillna(value=0,inplace=True)
    
#%%

#MIRI
hrsmiri=alldf[0].totPhoton.sum()
#NIRISS
hrsniriss=alldf[1].totPhoton.sum()
#NIRCam
nircam=alldf[2].totPhoton.sum()
#Nirspec MMOS
alldf[3].loc[alldf[3].tot5==" ",'tot5'] = 0
alldf[3].tot5.to_numeric()

totPhoton=alldf[3].tot1+alldf[3].tot2+alldf[3].tot3+alldf[3].tot4+alldf[3].tot5+alldf[3].tot6+alldf[3].tot7+alldf[3].tot8+alldf[3].tot9
df[3]['totPhoton']=totPhoton
#%%
            
#Nirspec FSS IFU
nirspecfss=alldf[4].

exoprog=(alldf[0].mode=='Coronography') | (alldf[0].mode)