# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:19:03 2015

@author: Kaddabadda

Get dates of events over chosen threshold
	*** save dates and precip sums to csv format to process in GIS
	*** calculate percentiles

"""
import numpy as np
import pandas as pd
import csv

def get_percentiles(dataframe):
    ''' calculate percentiles all data in frame (all stations, all times)
    *** output: [p95, p98, p99, p99.9]
    *** !!! ignores zeros !!!
    '''
    tet = dataframe.values
    tet[tet==0] = np.nan
    test = tet[pd.notnull(tet)]
    print len(test)
    percentiles_p3d = np.percentile(test, q=[95, 98, 99, 99.9])
    return percentiles_p3d


### function to read dates to csv file

def events_over_threshold(dataframe, threshold, filename, resample_interval):
    ''' Save dates of extreme events exceeding a defined threshold.
    
    INPUT:
    *** dataframe: dataframe with datetimeindex
    *** threshold: [mm] dates of periods with higher sums will be saved
    *** filename:  'str': name of file to be saved as csv and npy
    *** if resample_interval (str) is given, sums for given interval are
        calculated first.
    *** Input: '60Min', '1H', '24H' '1D', '3D'
    *** if no resampling required, pass '0' (int)
    
    OUTPUT:
    - destination directory is:
      r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Events_over_threshold'
    - returns dataframes of daily and hourly sums of all stations for the dates
      where at least one station exceeded the threshold
    - saves csv of dates, station ID and sums of highest station
    - transposed csv can be joined to a GIS station shapefile for visualization
    '''
    from itertools import izip
    path2file = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Events_over_threshold'
    csvname = filename + '.csv'
    
    if resample_interval == 0:
        print 'no resampling'
        dataframe_res = dataframe
    else:
        print 'resampling dataframe...'
        dataframe_res = dataframe.resample(resample_interval, how='sum',
                                           closed='left', label='left',
                                           base=0).dropna(axis=0, how='all')
   
    print 'finding events over threshold ...'
    dataframe_select = dataframe_res[dataframe_res > threshold].dropna(axis=0,
                                                                       how=
                                                                       'all')
    # datetime index of dataframe:
    idx = dataframe_select.index
    
    Dates = []
    Times = [] 
    # write csv file with date, daily sum, max hourly sum and max 10min intensity
    print 'Save dates of extreme precip intervals to csv ...'
    for i in range(len(idx)):
        formattedate = str(idx.day[i]) + '.' + str(idx.month[i]) + '.' + str(idx.year[i])
        formattedtime = str(idx.hour[i]) + ':' + str(idx.minute[i])
        Dates = np.append(Dates, formattedate)
        Times = np.append(Times, formattedtime)

    if Dates == []:
        day_tot_all = pd.DataFrame()
        hours_day_all = pd.DataFrame()
        print 'no extremes exceeding this threshold were found'
        return
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
                df_day_xtr_all = df_day_xtr
            else:
                day_tot_all = pd.concat([day_tot_all, day_tot], join='outer')
                hours_day_all = pd.concat([hours_day_all, hours_day], join='outer')
                df_day_xtr_all = pd.concat([df_day_xtr_all, df_day_xtr], join='outer')
 
    with open(path2file + '/Dates_' + csvname, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Time", "StationNrMaxDaily",
                         'MaxDaily',"StationNrMaxHourly", 'MaxHourly',
                         "StationNrMaxOrigFrame", 'MaxOrigFrame'])
        writer.writerows(izip(Dates, Times, day_tot_all.idxmax(axis=1).values,
                              np.round(day_tot_all.max(axis=1).values,2),
                              hours_day_all.idxmax(axis=1).values,
                              np.round(hours_day_all.max(axis=1).values,2),
                              df_day_xtr_all.idxmax(axis=1).values,
                              np.round(df_day_xtr_all.max(axis=1).values,2)))
    print 'Dates saved to directory ...\Python\Tables\Events_over_threshold'

   
    day_tot_all.to_pickle(path2file + '/daily_sums_' + filename + '.npy')
    hours_day_all.to_pickle(path2file + '/hourly_sums_' + filename + '.npy')     
    
    # write precip sums of days to transposed csv file to be joined to shpfile
    np.round(day_tot_all, 2).transpose().to_csv(path2file + '/DailySums_' +
                                                csvname, na_rep=
                                                0, index_label='synnr') #### na_rep = 'NaN'
    np.round(hours_day_all, 2).transpose().to_csv(path2file + '/HourlySums_' +
                                                  csvname, na_rep=
                                                  0, index_label='synnr') #### na_rep = 'NaN'
    print 'Saving daily and hourly sums of event to csv; '
    print 'formatted to be joined with station shape file in GIS'
    
    return day_tot_all, hours_day_all            
