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


pd.read(path2 + '/'+ outfile + '_wet_day_event_statistics.npy')
        idx = pd.IndexSlice        
        SumFrame = DayFrame.loc[idx[:], idx[:,'sum']]