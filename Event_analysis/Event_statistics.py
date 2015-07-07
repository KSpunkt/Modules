# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 11:22:16 2015

@author: Kaddabadda

*** Functions for basic statistic description of input dataframes
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Modules.Event_analysis.EventDates as ev

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\Data_describe'

ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min.npy')
AHYD_all_stations = pd.read_pickle(src + '\AHYD_dailysums.npy')




def describe_dataset(dataframe, res):
    ''' calculate basic statistics on 
    *** years, days, stations in record
    *** counts of NAN, Zero, drizzle, DWD intensity categories
    INPUT:
    *** pandas dataframe
    *** temporal resolution of df (thresholds depend on time steps)
    '''
    df = dataframe
    # use if only subset of months is considered
    #    month = df.index.month
    #    selector = ((4 <= month) & (month <= 10))
    #    df = df[selector]
    # 
    max_rec_len_years = df.index.year[-1]-df.index.year[0]+1
    total_rec = df.size

    # use thresholds depending on temporal resolution  
    thresholds = {'10min' : [0.1, 0.5, 1.7, 8.3, 17], '1h': [], '1d' : [], '3d'
                  : []}    
    
    
    for i in thresholds.values[res]:
        selector = df > i
        selected = df[selector]
        
        occurrence_days = selected.resample('D', how='sum', closed='left',
                                            label='left').dropna()
        nr_days_with_P = np.size(occurrence_days)
        
        percent_selected = np.round(np.float(np.size(selected))/
                                    np.float(np.size(df))*100, 2)
        
        
   # records greater 0.1mm
    mm_selector = df > 0.1
    wet = df[mm_selector]
    days_with_P = wet.resample('D', how='sum', closed='left', label='left').dropna()
    nr_days_with_P = np.size(days_with_P)
    # percent of total days to 'wet' days
    perc_wet_days = np.round(np.float(nr_days_with_P)/np.float(np.size(df.resample('D')))*100, 2)
    # percentage of wet records
    perc_wet = np.round(np.float(np.size(wet))/np.float(np.size(df))*100, 2)

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

    print 'Total record size: ', total_rec, ' instances \n'
    print 'Percent NaN: ', , '%\n'
    print 'Percent zeros: ', , '\n'
    print 'Percent wet (> 0.1mm)', , '\n'
    print 'Percent 0.1mm', , '\n'
    print 'Percent DWD light: ', , '\n'
    print 'Percent DWD moderate: ', , '\n'
    print 'Percent DWD heavy: ', , '\n'
    print 'Percent DWD very heavy: ', , '\n'
    print 'Percent "torrential": ', , '\n'


    # create stats dataframe with rows= statnrs and columns= length and percentages
    # last rows: mean and std??
    ZAMG_statistics.loc[zamg.statlist[i]] =  [rec_len_years, nr_days_with_P,
                                             perc_wet_days, total_rec,
                                             np.size(total_02mm), perc_wet, perc_zero, perc_nan,
                                             perc_drizzle]
    ZAMG_stats_float = pd.DataFrame(ZAMG_statistics, dtype='float')
    ZAMG_stats_float.describe()
    np.round(ZAMG_stats_float.describe(),2)


def temporal_distribution(dataframe, percentile):
    ''' get temporal distributions of extremes of categories (min, h, d, 3d)
    over time (year, month, day, hour of the day)
    '''
    df = dataframe
    # return index of the maximum values for each station
    max_dates_stations = dataframe.idxmax()       
    
    # Values of max intensities per station
    dates = pd.to_datetime(max_dates_stations.values)
    
    # peak intensity times
    plt.hist(dates.year)
    plt.hist(dates.month)
    plt.hist(dates.day)
    plt.hist(dates.minute)
    plt.hist(dates.hour)
    
    # days at which more than one station had its maximum
    # normalize index for min and h data?
    dup_dates = dates[dates.duplicated()]
    # which dates occur how often?
    dates.value_counts()



# dates over 99th percentile

  
    
dataframe.describe()
# how many valid records per station:
dataframe.count(0)
# how many valid records per date
dataframe.count(1)


# records / number of total daily sums in summer sample
total_sum = data.count(0).sum()

# DRIZZLE
drizzle_selector = (data < 0.2) & (data > 0)
drizzle_precip = data[drizzle_selector]
total_drizzle_days = drizzle_precip.count(0).sum()
# percentage of drizzle < 0.19mm/10min

# DRY DAYS
zero_selector = data==0
drydays = data[zero_selector]
total_drydays = drydays.count(0).sum()

# MISSING VALUES
nan_selector = pd.isnull(data)
nan_precip = data[nan_selector]
total_nan = nan_precip.count(0).sum()

# PRECIP GREATER 0.1mm/day
mm_selector = data > 0.1
total_02mm = data[mm_selector]
total_wet_days = total_02mm.count(0).sum()

perc_wet = np.float(total_wet_days)/np.float(total_sum) * 100.0

perc_drizzle = np.float(total_drizzle_days)/np.float(total_sum) * 100.0

perc_dry = np.float(total_drydays)/np.float(total_sum) * 100.0

greater100 = data[data>100]
greater100 = greater100.dropna(how='all')

# gives for each date the station that had the highest value for the day
data.idxmax(axis=1)

# for each station the date where the station had its max
data.idxmax(axis=0)   