# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:43:43 2015

@author: Kaddabadda
"""

import numpy as np
import pandas as pd
import glob
''' class to extract day and hour events and max daily temperatures'''
import Modules.Event_analysis.EventFrameClass_HRStations_SpartacusT as ev

ZAMG_p  = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\Station_Dataframes\ZAMGStationSeries'
AHYD_p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution\edited_for_processing\AHYDStationSeries'

allFiles = glob.glob(ZAMG_p + '\*.npy') + glob.glob(AHYD_p + '\*.npy')

for station in allFiles:
    dataIn = pd.read_pickle(station)
    '''as of NOv 15, SPARTACUS data until 2011'''
    dataIn = dataIn[dataIn.index.year<2012]
    '''EventFrame, resample AHYD to 10min'''
    EF = ev.Eventframe(dataIn, '10min', season=[3,11], resampling='10min', valid=1)
    ''' get day events'''
    DF = EF.EventDays('testout', valid=0, wet_day_threshold=1)
    ''' get hour events'''
    HF = EF.EventHours(DF, 'testout2', wet_hour_threshold=.2, valid=0)


import matplotlib.pyplot as plt
plt.plot(HF.index.hour, HF['peak 1'], 'o')
plt.plot(HF['Tmax_a'], HF['peak 1'], 'o')
plt.plot(HF['Tmax_b'], HF['peak 1'], 'o')

HF_short = HF[HF['duration']<5]
plt.plot(HF_short['Tmax_a'], HF_short['peak 1'], 'o')
plt.plot(HF_short['Tmax_b'], HF_short['peak 1'], 'o')


HF_long = HF[HF['duration']>5]
plt.plot(HF_long['Tmax_a'], HF_long['peak 1'], 'o')
plt.plot(HF_long['Tmax_b'], HF_long['peak 1'], 'o')


HF_long = HF[HF.index.hour>12]
plt.plot(HF_long['Tmax_a'], HF_long['peak 1'], 'o')
plt.plot(HF_long['Tmax_b'], HF_long['peak 1'], 'o')

HF_long = HF[HF.index.hour<12]
plt.plot(HF_long['Tmax_a'], HF_long['peak 1'], 'o')
plt.plot(HF_long['Tmax_b'], HF_long['peak 1'], 'o')