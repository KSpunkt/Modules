# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 08:21:18 2015

@author: Kaddabadda
"""

import Modules.ZAMG_tawes.stationfiles_v9 as zamg
import numpy as np
import pandas as pd

emptylist = []
pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
# preallocate statistics dataframe


for eachStation in zamg.statlist:
    statnr = int(eachStation)
    print 'processing statnr: ', statnr

    df = pd.read_csv(pth2 + '\DataFrame_' + str(statnr) + '.csv', index_col=0,
                     usecols=[0,'precip'], parse_dates=True)

    # selector extended summer months AMJJASO
    month = df.index.month
    selector = ((1 <= month) & (month <= 12))
    data = df.iloc[:,[0]][selector] #precip[selector]
    data.columns = [eachStation]
    del df
    emptylist.append(data)

ZAMG_all_stations = pd.concat(emptylist, axis=1)

ZAMG_all_stations.to_pickle(pth2 + '\ZAMG_10min_allyear.npy')


emptylist = []
pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
# preallocate statistics dataframe


for eachStation in zamg.statlist:
    statnr = int(eachStation)
    print 'processing statnr: ', statnr

    df = pd.read_csv(pth2 + '\DataFrame_' + str(statnr) + '.csv', index_col=0,
                     usecols=[0,'precip'], parse_dates=True)

    # selector extended summer months AMJJASO
    month = df.index.month
    selector = ((4 <= month) & (month <= 10))
    data = df.iloc[:,[0]][selector] #precip[selector]
    data.columns = [eachStation]
    del df
    emptylist.append(data)

ZAMG_all_stations = pd.concat(emptylist, axis=1)

ZAMG_all_stations.to_pickle(pth2 + '\ZAMG_10min_Apr-Oct.npy')

''' SOME BASIC STATISTICS
'''
    # days in summer sample
    rec_len_years = data.index.year[-1]-data.index.year[0]+1
    total_rec = data.size

    # records greater 0.1mm
    mm_selector = data > 0.1
    total_02mm = data[mm_selector]
    days_with_P = total_02mm.resample('D', how='sum', closed='left', label='left').dropna()
    nr_days_with_P = np.size(days_with_P)
    # percent of total days to 'wet' days
    perc_wet_days = np.round(np.float(nr_days_with_P)/np.float(np.size(data.resample('D')))*100, 2)
    # percentage of wet records
    perc_wet = np.round(np.float(np.size(total_02mm))/np.float(np.size(data))*100, 2)

    zero_selector = data==0
    positive_precip = data[zero_selector]
    # percentage of zero
    perc_zero = np.round(np.float(np.size(positive_precip))/np.float(np.size(data))*100, 2)

    nan_selector = pd.isnull(data)
    nan_precip = data[nan_selector]
    # percentage of nan
    perc_nan = np.round(np.float(np.size(nan_precip))/np.float(np.size(data))*100, 2)

    drizzle_selector = (data < 0.2) & (data > 0)
    drizzle_precip = data[drizzle_selector]
    # percentage of drizzle < 0.19mm/10min
    perc_drizzle = np.round(np.float(np.size(drizzle_precip))/np.float(np.size(data))*100, 2)



    # create stats dataframe with rows= statnrs and columns= length and percentages
    # last rows: mean and std??
    ZAMG_statistics.loc[zamg.statlist[i]] =  [rec_len_years, nr_days_with_P,
                                             perc_wet_days, total_rec,
                                             np.size(total_02mm), perc_wet, perc_zero, perc_nan,
                                             perc_drizzle]
    ZAMG_stats_float = pd.DataFrame(ZAMG_statistics, dtype='float')
    ZAMG_stats_float.describe()
    np.round(ZAMG_stats_float.describe(),2)
