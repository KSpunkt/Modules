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
        
def EventDays(self, outfile):
    '''
    Function to filter dry and wet (sum > 1mm) days
    - counts the events of wet days -> consecutive wet days are one event
    - calculates first statistics on the day-based events
    '''
    
    # resampling ensures that the timestamp of the datetime index is the same
    # WARNING: 7-7am recordings will be assigned 0-24h
    
    df_values = self.dataframe.resample('1D', how='sum',closed='left', label='left',
                                    base=0)           
    
                       
    df_daily = self.dataframe.resample('1D', how='sum',closed='left', label='left',
                                    base=0)
    # assign dry (0) and wet days (1) 
    df_daily[df_daily >= 1] = 1
    df_daily[df_daily < 1] = 0  
    
    # preallocate list where Event ID data will be stored
    listall = [0] * len(df_daily.columns.values)
    
    # loop through all stations in the dataset
    for station, loop in zip(df_daily.columns.values, range(len(df_daily.columns.values))):
        print loop, 'st/th station processed (', station, ')'
        # treat each station as series
        Series = df_daily[station]
        
        
        count = 0
        array_event = []
        
        # loop through observations in each station series
        for x, t in zip(Series, range(len(Series))):
            print 'step: ', t, ' value: ', x
            # if first observation is positive don't check for preceding day
            if np.logical_and(t==0, x>0):
                count = count+1
                array_event.append(count)
                
            else:
                # assign NaN for dry days
                if x==0:
                    array_event.append(np.nan)
                    
                # assign an event ID for wet days
                else:
                    # assign the same event ID for consecutive wet days
                    if Series[t-1] != 0:
                        array_event.append(count)
                    # assign new event ID if a dry day preceded the wet day
                    else:
                        count = count+1
                        array_event.append(count)
          
        # print array_event
        '''for each station record add the event ID column, which attributes a
        number to events of consecutive wet days if at least one zero or NaN
        day is in between
        '''
        df = pd.DataFrame({station: df_values[station], station + '_eventID': array_event})
        byEvent = df.groupby[station + '_eventID']
        byEvent.agg([np.sum, np.mean, len, np.max])
        
        
        listall[loop] = df
    
    
    # save the dataframe of all stations and event IDs
    DF_all = pd.concat(listall, axis=1)
    DF_all.to_pickle(self.path2 + '/'+ outfile + '_wet_day_events.npy')

               


























          