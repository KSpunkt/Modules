# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:19:03 2015

@author: Kaddabadda

Get dates of events that will enter sample of in depth analysis
	*** save dates and precip sums to csv format to process in GIS
	*** calculate percentiles

"""


#runfile('I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes/stationfiles_v9.py', wdir='I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes')
#runfile()
import matplotlib as mpl

import numpy as np
import pandas as pd
import csv
import os
import numpy.ma as ma
import matplotlib.pyplot as plt
import Modules.ZAMG_tawes.stationfiles_v9 as zamg
import matplotlib.dates as dates
import Modules.ZAMG_tawes.plotting.plot_99percentile_events as zamgplot
import scipy.stats as ss


# all observations > 1.9mm/10min (AMJJASO)
# df_gr019mm = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\p_greater_019m_all.npy')

def percentiles_totsample(dataframe):
    ''' calculate percentiles all data in frame (all stations, all times)
    *** output: [p95, p98, p99, p99.9]
    '''
    tet = dataframe.values
    tet[tet==0] = np.nan
    test = tet[pd.notnull(tet)]
    print len(test)
    percentiles_p3d = np.percentile(test, q=[95, 98, 99, 99.9])
    return percentiles_p3d


### function to read dates to csv file

def datimeIndex_to_csv(dataframe, threshold, filename, resample_interval):
    ''' save dates and time of extreme time periods in dataframe to csv file
    and a csv to be joined to the station shapefile for GIS visualization
    *** dataframe: input dataframe of data
    *** threshold: [mm] dates of periods with higher sums will be saved
    *** filename:  'str': name of file to be saved
    *** if resample_interval (str) is given, sums for given interval are calculated
        first.
        *** Input: '60Min', '1H', '24H' '1D', '3D'
        *** if no resampling required, pass '0' (int)
    '''

    if resample_interval == 0:
        print 'no resampling'
        dataframe_res = dataframe
    else:
        print 'resampling dataframe...'
        dataframe_res = dataframe.resample(resample_interval, how='sum',
                                           closed='left', label='left',
                                           base=0).dropna(axis=0, how='all')

    from itertools import izip
    path2file = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Tables_of_extremes_samples'
    filename = filename + '.csv'
    print 'extract values over threshold ...'
    dataframe_select = dataframe_res[dataframe_res > threshold].dropna(axis=0,
                                                                       how=
                                                                       'all')
    # datetime index of dataframe:
    idx = dataframe_select.index
    Dates = []
    Times = []
    print 'Save dates of extreme precip intervals ...'
    for i in range(len(idx)):
        formattedate = str(idx.day[i]) + '.' + str(idx.month[i]) + '.' + str(idx.year[i])
        formattedtime = str(idx.hour[i]) + ':' + str(idx.minute[i])
        Dates = np.append(Dates, formattedate)
        Times = np.append(Times, formattedtime)
        with open(path2file + '/Dates_' + filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(izip(Dates, Times))
    print 'File saved to directory Python/Tables/Tables of extremes/samples.'

    if Dates == []:
        day_tot_all = pd.DataFrame()
        hours_day_all = pd.DataFrame()
        print 'no such extremes in sample'
    else:
        print 'Calculate daily and hourly sums days with extreme periods'
        for i in range(len(Dates)):
            day = str(idx.year[i]) + '-' + str(idx.month[i]) + '-' + str(idx.day[i])
            df_day_xtr = dataframe[day]
            # sum up all 10min bin from one day
            day_tot = df_day_xtr.resample('D', how='sum', closed='left',
                                          label='left', base=0)
            hours_day = df_day_xtr.resample('H', how='sum', closed='left',
                                            label='left', base=0)
            if i == 0:
                day_tot_all = day_tot
                hours_day_all = hours_day
            else:
                day_tot_all = pd.concat([day_tot_all, day_tot], join='outer')
                hours_day_all = pd.concat([hours_day_all, hours_day], join='outer')

    # write precip sums of days to transposed csv file to be joined to shpfile
    np.round(day_tot_all, 2).transpose().to_csv(path2file + '/DailySums' +
                                                filename, na_rep=
                                                0, index_label='synnr') #### na_rep = 'NaN'
    np.round(hours_day_all, 2).transpose().to_csv(path2file + '/HourlySums' +
                                                  filename, na_rep=
                                                  0, index_label='synnr') #### na_rep = 'NaN'
    print 'Sums saved to csv to be joined with station shape file in GIS'

def datimeIndex_to_csv_over_percentile(dataframe, p, filename, resample_interval):
    ''' save dates and time of extreme time periods in dataframe to csv file
    and a csv to be joined to the station shapefile for GIS visualization
    *** dataframe: input dataframe of data
    *** p: dates of periods with sums over percentile
        0: p95
        1: p98
        2: p99
        3: p99.9

    *** filename:  'str': name of file to be saved
    *** if resample_interval (str) is given, sums for given interval are calculated
        first.
        *** Input: '60Min', '1H', '24H' '1D', '3D'
        *** if no resampling required, pass '0' (int)
    '''

    if resample_interval == 0:
        print 'no resampling'
        dataframe_res = dataframe
    else:
        print 'resampling dataframe...'
        dataframe_res = dataframe.resample(resample_interval, how='sum',
                                           closed='left', label='left',
                                           base=0).dropna(axis=0, how='all')
    # get percentile value over which to choose sample
    threshold = percentiles_totsample(dataframe_res)[p]
    print 'percentile value: ', threshold

    from itertools import izip
    path2file = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Tables_of_extremes_samples'
    path2file_joins = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Tables_of_extremes_samples_joins'

    filename = filename + '.csv'
    print 'extract values over threshold ...', threshold
    dataframe_select = dataframe_res[dataframe_res > threshold].dropna(axis=0,
                                                                       how=
                                                                       'all')
    # datetime index of dataframe:
    idx = dataframe_select.index
    Dates = []
    Times = []
    print 'Save dates of extreme precip intervals ...'
    for i in range(len(idx)):
        formattedate = str(idx.day[i]) + '.' + str(idx.month[i]) + '.' + str(idx.year[i])
        formattedtime = str(idx.hour[i]) + ':' + str(idx.minute[i])
        Dates = np.append(Dates, formattedate)
        Times = np.append(Times, formattedtime)
        with open(path2file + '/Dates_' + filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(izip(Dates, Times))
    print 'File saved to directory Python/Tables/Tables of extremes/samples.'

    if Dates == []:
        day_tot_all = pd.DataFrame()
        hours_day_all = pd.DataFrame()
        print 'no such extremes in sample'
    else:
        print 'Calculate daily and hourly sums days with extreme periods'
        for i in range(len(Dates)):
            day = str(idx.year[i]) + '-' + str(idx.month[i]) + '-' + str(idx.day[i])
            df_day_xtr = dataframe[day]
            # sum up all 10min bin from one day
            day_tot = df_day_xtr.resample('D', how='sum', closed='left',
                                          label='left', base=0)
            hours_day = df_day_xtr.resample('H', how='sum', closed='left',
                                            label='left', base=0)
            ''' create one table for each day with 24 fields,
            otherwise attribute table becomes to long
            '''
            np.round(hours_day, 2).transpose().to_csv(path2file_joins + '/HourlySums'
                                                      + day + filename, na_rep=
                                                      0, index_label='synnr') # header=range(hours_day.shape[0])

            if i == 0:
                day_tot_all = day_tot
                hours_day_all = hours_day
            else:
                day_tot_all = pd.concat([day_tot_all, day_tot], join='outer')
                hours_day_all = pd.concat([hours_day_all, hours_day], join='outer')

    # write precip sums of days to transposed csv file to be joined to shpfile
    np.round(day_tot_all, 2).transpose().to_csv(path2file_joins + '/DailySums' +
                                                filename, na_rep=
                                                0, index_label='synnr') #### na_rep = 'NaN'

    np.round(hours_day_all, 2).transpose().to_csv(path2file + '/HourlySums' +
                                                  filename, na_rep=
                                                  0, index_label='synnr') #### na_rep = 'NaN', ###header=range(hours_day_all.shape[0])

    print 'Sums saved to csv to be joined with station shape file in GIS'


def datimeIndex_to_dataframes(dataframe, p, filename, resample_interval):
    ''' save dates and time of extreme time periods in dataframe to npy
    for further analysis and plotting in python
    *** dataframe: input dataframe of data
    *** p: dates of periods with sums over percentile
        0: p95
        1: p98
        2: p99
        3: p99.9

    *** filename:  'str': name of file to be saved
    *** if resample_interval (str) is given, sums for given interval are calculated
        first.
        *** Input: '60Min', '1H', '24H' '1D', '3D'
        *** if no resampling required, pass '0' (int)
    '''

    if resample_interval == 0:
        print 'no resampling'
        dataframe_res = dataframe
    else:
        print 'resampling dataframe...'
        dataframe_res = dataframe.resample(resample_interval, how='sum',
                                           closed='left', label='left',
                                           base=0).dropna(axis=0, how='all')
    # get percentile value over which to choose sample
    threshold = percentiles_totsample(dataframe_res)[p]

    from itertools import izip
    path2file = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\Percentile_samples_p999'
    filename = filename + '.npy'

    print 'extract values over threshold ...'
    dataframe_select = dataframe_res[dataframe_res > threshold].dropna(axis=0,
                                                                       how=
                                                                       'all')
    # datetime index of dataframe:
    idx = dataframe_select.index
    Dates = []
    Times = []
    print 'Save dates of extreme precip intervals ...'
    for i in range(len(idx)):
        formattedate = str(idx.day[i]) + '.' + str(idx.month[i]) + '.' + str(idx.year[i])
        formattedtime = str(idx.hour[i]) + ':' + str(idx.minute[i])
        Dates = np.append(Dates, formattedate)
        Times = np.append(Times, formattedtime)
    print Dates 
    if Dates == []:
        day_tot_all = pd.DataFrame()
        hours_day_all = pd.DataFrame()
        print 'no such extremes in sample'
    else:
        print 'Calculate daily and hourly sums days with extreme periods'
        print Dates
        for i in range(len(Dates)):
            day = str(idx.year[i]) + '-' + str(idx.month[i]) + '-' + str(idx.day[i])
            df_day_xtr = dataframe[day]
            # sum up all 10min bin from one day
            day_tot = df_day_xtr.resample('D', how='sum', closed='left',
                                          label='left', base=0)
            # sum up all 10min bin from one hour in each day an extreme occurred
            hours_day = df_day_xtr.resample('H', how='sum', closed='left',
                                            label='left', base=0)
            if i == 0:
                day_tot_all = day_tot
                hours_day_all = hours_day
            else:
                day_tot_all = pd.concat([day_tot_all, day_tot], join='outer')
                hours_day_all = pd.concat([hours_day_all, hours_day], join='outer')
                
    day_tot_all.to_pickle(path2file + '/daily_total_' + filename + '.npy')
    hours_day_all.to_pickle(path2file + '/hourly_total_' + filename+ '.npy')
    return Dates, Times, day_tot_all, hours_day_all