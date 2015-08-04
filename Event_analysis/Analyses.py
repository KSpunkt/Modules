# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:04:11 2015

@author: Kaddabadda
"""
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from itertools import izip
import Modules.Event_analysis.Event_statistics as es

path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_heatmaps'


AHYD_all_stations = pd.read_pickle(src + '\AHYD_dailysums.npy')
ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min_allyear.npy')


import Modules.Event_analysis.Event_statistics as es

ZAMG = es.Eventframe(ZAMG_all_stations.loc['2010'], resolution='10min', 
                     season=[6,8])
                     
Dayframe = ZAMG.EventDays('test_ZAMG_10min_JJA_2010') 



Hourframe = ZAMG.EventHours(Dayframe, 'test_ZAMG_10min_JJA_2010')       



Dayframe.xs('max daily', level=1, axis=1).max(axis=1).order(ascending=False)


#pd.read(path2 + '/'+ outfile + '_wet_day_event_statistics.npy')
#        idx = pd.IndexSlice        
#        SumFrame = DayFrame.loc[idx[:], idx[:,'sum']]


peak1 = Dayframe.xs('peak 1', level=1, axis=1).max(axis=1).order(ascending=False)
duration = Dayframe.xs('duration', level=1, axis=1).max(axis=1).order(ascending=False)


peak1 = Dayframe.xs('peak 1', level=1, axis=1)
duration = Dayframe.xs('duration', level=1, axis=1)

for station in Dayframe.columns.get_level_values(0):
    plt.plot(Dayframe[station].duration.values, Dayframe[station]['peak 1'].values, marker='x', linestyle='')
    plt.xlim([0,10])
    plt.ylim([0,50])
    
for [i, station] in enumerate(Hourframe.columns.get_level_values(0)):
    plt.plot(Hourframe[station].duration.values, Hourframe[station]['peak 1'].values, marker='x', linestyle='')
    plt.xlim([0,20])
    plt.ylim([0,30])
    print i
    ''' ONLY 76 stations have peak values - why!?
    '''