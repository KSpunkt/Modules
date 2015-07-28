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
import itertools

# initial thresholds

def Events(self):
    ''' get detailed event information stationwise
    - start point
    - end point
    - peak intensity
    - number of NAN
    - cumulative sum
    - duration
    '''
    thresholds = {'5min': 0.1, '10min': 0.1, '30min':2.5, '1h': 0.1, '1D': 10}

    for Station in pd.DataFrame.columns.values:
    
        Series = pd.DataFrame[pd.DataFrame[Station]]

    
        for y, nr in zip(Series, range(len(Series)-6)):
            # starting point conditions: at least two positive values and at least
            # a threshold value in 30 min
            
            if np.logical_and(Series[nr] >= thresholds['5min'], np.logical_and(
                              Series[nr+1] >= thresholds['5min'],
                              Series[nr:nr+5].sum() > thresholds['30min'])):
                
                print 'potential start point', Series.index[nr]
                
                # if this condition is met 
                # count all positive values into Event array until a zero shows up  
                count = 0
                for x in Series[nr:-1]:                
                    
                    if x != 0:
                        print x
                    else:
                        print 'zero'
    
    # if a daily sum is > 1mm and an hour is > .2mm
        


               

'''
event Dataframe
# INDICES
level1 = stations # index 1

level2 = event ID

idx = pd.MultiIndex.





















          