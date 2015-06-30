# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 11:22:16 2015

@author: Kaddabadda

*** read the dates of the heaviest p99.9 events, look at basic distribution of events in time of the year/month/day
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Modules.ZAMG_tawes.Sample_definition as eventdates

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'

ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min.npy')
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_PDFs'


AHYD_all_stations = pd.read_pickle(src + '\AHYD_allstations_summer.npy')

# deletes the time stamp 07:00:00 from Datetime index
# maybe not useful because now it plots from 00:00 - 00:00 which is wrong
# AHYD_all_stations.index = pd.DatetimeIndex(AHYD_all_stations.index).normalize()

# save the dates of daily sums over 99.9t percentile (3)
eventdates.datimeIndex_to_csv_over_percentile(AHYD_all_stations, 3, 'AHYD_p999',
                                              0)

eventdates.datimeIndex_to_csv_over_percentile(ZAMG_all_stations, 3,
                                              'ZAMG_p999_1H', '1H')

max_dates_stations = ZAMG_all_stations.idxmax()
# Values of max intensities per station
xxx = pd.to_datetime(max_dates_stations.values)
max_intensity_hours = xxx.hour

# peak intensity times
plt.hist(xxx.month)
plt.hist(xxx.day)
plt.hist(xxx.minute)
plt.hist(xxx.hour)

ZAMG_all_stations['2011-07-07'].plot(legend=False)

AHYD_all_stations['2011-07-06':'2011-07-08'].plot(legend=False)

# dates where each station had its max
max_dates_AHYDstations = AHYD_all_stations.idxmax()
yyy = pd.to_datetime(max_dates_AHYDstations.values)
plt.hist(yyy.month)
plt.hist(yyy.day)
# days at which more than one station had its maximum
yyy[yyy.duplicated()]
# which dates occur how often?
yyy.value_counts()

# dates over 99th percentile