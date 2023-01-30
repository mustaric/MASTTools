#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:40:34 2018

@author: smullally
"""

import scipy.io as spio

#Examine the PRFS.
filename="/Users/smullally/TESS/engineering/PRF/tess2018243163600-00072_035-1-2-characterized-prf.mat"


mat = spio.loadmat(filename,matlab_compatible=True)
mat.keys()

#%%

prfstruct=mat['prfStruct']