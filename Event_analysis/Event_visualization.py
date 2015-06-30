# -*- coding: utf-8 -*-
"""
Created on Sun Jun 07 12:50:23 2015

@author: Kaddabadda

*** EVENT VISUALISATION***
---- get dates where intensities over 99.9th percentile have been recorded

		*** input: raw station data for the entire year
		*** classes ZAMG: 10min, 1h, 1d, 7am-7am, 3d, 3d 7am-7am
		*** classes AHYD daily (eHyd): 7am-7am
		*** identify and write to file dates of events > 99.9th percentile
		*** extract three days around the events
	    *** sum up event precipitation and save with header
        *** event number
        *** latitude and longitude of station
		*** save plot of intesity matrices 
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Modules.Event_analysis.plotting.intensity_matrix_colorbar as im
import Modules.ZAMG_tawes.EventDates as smp

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_heatmaps'


AHYD_all_stations = pd.read_pickle(src + '\AHYD_allstations_summer.npy')
ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min_allyear.npy')


percentiles_ZAMG_YR = smp.percentiles_totsample(ZAMG_all_stations)

[Dates, Times, day_tot_all, hours_day_all] = smp.datimeIndex_to_dataframes(ZAMG_all_stations,
                                             3, 'ZAMGp999YR_1d', '1D')

# Mariapfarr crazy Rain
ZAMG_all_stations['11348']['19970703'].loc[ZAMG_all_stations['11348']['19970703']>30] = np.nan
ZAMG_all_stations['11348']['19970704'].loc[ZAMG_all_stations['11348']['19970704']>30] = np.nan
ZAMG_all_stations['11265']['20060802'].loc[ZAMG_all_stations['11265']['20060802']>50] = np.nan

# make list of dates
dates = ['1995-09-04', '1999-07-22', '2002-06-06', '2003-08-28', '2007-09-07',
         '2009-09-04', '2008-07-14', '2008-08-15', '2009-07-18', '2009-08-22',
         '2010-05-05', '2010-07-15', '2010-07-17', '2011-08-03', '2012-09-12',
         '2013-08-09', '2014-08-31']

#dates = ['1995-09-04', '1999-07-22']
for date in dates:
    event = ZAMG_all_stations[date]
  
    # 1: N-S, 2: W-E
    #im.event_matrix(event, 1, 'E_NW_' + date)
    im.event_matrix(event, 2, 'E_WE_' + date)

    

'''
for record in testevent.values:
    if record == 0 or record == None:
        print 'trocken!'
        pass
    elif record > 0.1:
         
        print 'Regen!'

# do cumsum
# if 2 in 3 are positive?
for statnr in testevent.columns:
    for time in testevent.index:
        
        while testevent[statnr][time] > 0.1
        record = testevent[statnr]
    print 'this is', statnr, 'at', timestep, testevent[statnr][timestep]
    if testevent[statnr][timestep] == None:
        print 'REGEN!'
'''        
        resamples = ['1H', '1D', '3D'] #[0, '1H', '1D', '3D']
p = 3 # mm precip in time span
# a possibility is to use the eprcentile values from func above s thresholds
filenames = ['xtr_1H_p999', 'xtr_1D_p999', 'xtr_3D_p999']# ['xtr_10minp999', 'xtr_1H_p999', 'xtr_1D_p999', 'xtr_3D_p999']

for h, i in zip(filenames, resamples):
    spl.datimeIndex_to_csv_over_percentile(df_gr019mm, p, h, i)


# get dates over 99.9th percentile of total samples to npy dataframes!

resamples = [0, '1H', '1D', '3D'] #[0, '1H', '1D', '3D']
p = 3 # mm precip in time span
# a possibility is to use the eprcentile values from func above s thresholds
filenames = ['xtr_10min_p999', 'xtr_1H_p999', 'xtr_1D_p999', 'xtr_3D_p999']# ['xtr_10minp999', 'xtr_1H_p999', 'xtr_1D_p999', 'xtr_3D_p999']

for h, i in zip(filenames, resamples):
    spl.datimeIndex_to_dataframes(df_gr019mm, p, h, i)

# correlation!?!