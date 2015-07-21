# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 08:56:55 2015

@author: Kaddabadda

EVENT DETECTION ALGORITHM
"""
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from itertools import izip


thresholds = {'5min': 0.1, '10min': 0.1, '1h': [], '1D': 10}

it=0
for Station in pd.DataFrame.columns.values:

    Series = pd.DataFrame[pd.DataFrame[Station]]


    for y, nr in zip(Series, range(len(Series))):
        
        if np.logical_and(Series[nr] >= .1, np.logical_and(Series[nr+1] >= .1, Series[nr:nr+5].sum() > 2.5)):
            
            print 'potential start point', Series.index[nr]
        while Series[nr] >= .1:
            nr = nr+1
        
        # start moving average sum in [1h] >
            break
        
        nr = nr+1 
            
            
        if Series[x] >= 4.1:
            print 'potential starting point'
            Series[x+1] >= .1
            
        else:
            x = x+1
            
    
    if np.any():
        
        np.cumsum()
        
        for idx, row in data.iterrows():
        pass