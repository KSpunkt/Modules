# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:19:03 2015
edited 2015 07 13
@author: Kaddabadda
"""
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from itertools import izip



def resample_valid(df, res, valid, **kwargs):    
    ''' 
    METHOD:
    * resamples DataFrame with resample function
    * rows where number of missing values exceed threshold can be set to NaN
    -----------------------------------------------------------------------
    INPUT:
    * df: pd.DataFrame
    * res: resolution to be resampled to
    * valid: Minimum number of valid values per resample interval
      e.g.: 10min to 1H: '5' --> 5 out of 6, 1 NaN per hour accepted
    * ** kwargs: pass resample arguments
    -----------------------------------------------------------------------
    OUTPUT:
    * resampled DataFrame where intervals with too few valid data points are
      set to NaN
    -----------------------------------------------------------------------
    '''
    Ser_D = {}
    df1 = df.resample(res, how=[np.sum, pd.Series.count], closed='left',
                     label='left', **kwargs)
    # drop all rows where the count != len
    querystr = 'count >= ' + str(valid)
    print 'query string: ', querystr
    counter = 0
    for station in df.columns.get_level_values(0).drop_duplicates():
        counter = counter + 1
        #print 'processing station ', station
        # print counter
        Series = df1[station].query(querystr)
        if Series.empty:
            Series = df1[station]['sum']
            Ser_D.update({station: Series})
        else:
            # re-insert NaN for dropped rows and rename column
            Series = Series['sum']
            Series = Series.resample(res)
            Ser_D.update({station: Series})
   
    df_new = pd.concat(Ser_D, axis=1)
    df_new.columns = df_new.columns.get_level_values(0).drop_duplicates()
    return df_new


class Eventframe:
    ''' 
    ------------------------------------------------
    Methods to analyse observed station net datasets and identify extremes
    ------------------------------------------------
    
    Instance = Events(pd.DataFrame)
    
    '''  
    
    def __init__(self, dataframe, resolution='10min', season=[1, 12],
                 resampling=False, valid=0):
        ''' 
        METHOD:
        * class instance stationfiles (n=len(statnrs)*len(yrs))
        -----------------------------------------------------------------------
        Class  attributes / INPUT:
        * dataframe: pd.DataFrame with DateTime Index      
        * resolution: temporal resolution of dataframe (frequency of pd.dataFrame)
                    default: '10min'
        * season: first and last month to be included in the DataFrame
        * resampling: resample Dataframe to other temporal resolution
                    default: False
                    options: '10min', '60Min', '1H', '24H' '1D', '3D'
        * valid: minimum number of valid datapoints in resample interval, 
          default = 0
        -----------------------------------------------------------------------
        OUTPUT:
        * Instance of Class
        -----------------------------------------------------------------------
        '''
        
        self.resolution = resolution
        self.resampling = resampling
        self.season = season
        self.valid = valid
        
        
        self.path1 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis'
        self.path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'
        self.path3 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description'
        self.path4 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description\Plots'
        
        month = dataframe.index.month
        selector = ((season[0] <= month) & (month <= season[1]))
        self.dataframe = dataframe[selector] 
        self.rawinputdata = dataframe[selector]        
        
        if resampling == False:
            print 'no resampling'
        else:
            print 'resampling dataframe to ', self.resampling
            self.dataframe = resample_valid(self.dataframe, self.resampling,
                                            valid = self.valid, base=0).dropna(axis=0,
                                                                         how=
                                                                         'all')
                                                        
        # Thresholds selectors: boolean matrices returning selection              
        self.thres_sel = {'5min' : {'heavy Wussow (>=5)': self.dataframe>=5,
                                    'heavy Schimpf (>= 7.5)': self.dataframe>=7.5,
                                    'heavy DWD (>=5)': self.dataframe>=5},
                          '10min' : {'drizzle (==.1)': self.dataframe==.1,
                                     'light (>.1 & <.5)': (self.dataframe>.1) &
                                     (self.dataframe<.5),
                                     'moderate (>.5 & < 1.7)': (self.dataframe>= .5) &
                                     (self.dataframe<1.7),
                                     'heavy (>=1.7 & < 8.3)': (self.dataframe>=1.7) &
                                     (self.dataframe<8.3),
                                     'very heavy (>= 8.3)': self.dataframe>=8.3,
                                     'torrential (>17)': self.dataframe>17},
                          '1H': {'drizzle (>.1 & <.5)': (self.dataframe>.1) &
                                 (self.dataframe<.5),
                                 'light (>= .5 & < 2.5)': (self.dataframe>=.5) &
                                 (self.dataframe<2.5),
                                 'moderate (>=5 & <10):': (self.dataframe>=2.5) &
                                 (self.dataframe<10),
                                 'heavy (>=10)': self.dataframe>=10,
                                 'very heavy (>=50)': self.dataframe>=50},
                          '1D' : {'Schimpf (35)': self.dataframe>=35,
                                  'Wussow (84.9)': self.dataframe>=84.9},
                          '3D' : {'Carinthian (>=177)': self.dataframe>=177}}
             
        #df_statistics = self.dataframe.describe(percentiles=[.5, .9, .999])
             
        # Number of stations in dataset:
        self.nr_stations = len(self.dataframe.columns)
        
        # numbers on the lengths of the series of the stations
        records = []
        for eachCol in self.dataframe.columns:
            series = self.dataframe[eachCol].dropna()
            if series.empty:
                rec_len = np.nan
                records.append(rec_len)
            else:
               rec_len = len(range(series.index.year[0], series.index.year[-1]+1))
               records.append(rec_len)
        records = np.hstack(records)
        
        self.years = {'longest':[records.max()], 
                 'shortest':[records.min()],
                 'mean': [records.mean()],
                 'median':[np.median(records)],
                 'cumulative':[records.sum()]}
                 
        # numbers of records exceeding p99 and p99.9          
        self.occurrences = {'>p99' : self.dataframe[self.dataframe > self.get_percentiles()['p99']['value']].count(0).sum(),
                       '>p99.9' : self.dataframe[self.dataframe > self.get_percentiles()['p99.9']['value']].count(0).sum(),
                       '>0': self.dataframe[self.dataframe>0].count(0).sum(),
                       '0' : self.dataframe[self.dataframe==0].count(0).sum()}
        
        # count the instances fulfilling each selection criterion
        if self.resampling == False:
            key = self.resolution
        else:
            key = self.resampling
            
        occ_over_thres = {}    
        for subkey in self.thres_sel[key].keys():                       
                nr = self.dataframe[self.thres_sel[key][subkey]].count(0).sum()
                occ_over_thres[(str(key)+ ' ' + str(subkey))] = nr
        self.occ_over_thres = occ_over_thres        
      
    def get_percentiles(self):
        ''' 
        METHOD:
        * calculate percentiles all data in frame (all stations, all times)
        * !!! ignores zeros !!!
        -----------------------------------------------------------------------
        INPUT:
        * DataFrame instance of class
        -----------------------------------------------------------------------
        OUTPUT:
        * [p95, p98, p99, p99.9]
        * and number of occurrences over percentile
        -----------------------------------------------------------------------
        '''
        tet = self.dataframe.values
        tet[tet==0] = np.nan
        test = tet[pd.notnull(tet)]
        print 'Observations > 0: ', len(test)
        p3d = np.percentile(test, q=[95, 98, 99, 99.9])
        nr = []
        for value in p3d:    
            select = test > value
            nr.append(len(test[select]))
        percentiles_dict = {'p95':{'value': p3d[0], 'nr': nr[0]}, 'p98':{'value':
                             p3d[1], 'nr': nr[1]}, 'p99':{'value':p3d[2], 'nr':
                             nr[2]}, 'p99.9':{'value':p3d[3], 'nr':nr[3]}}
        print 'percentiles and number of observaitons above: \n', percentiles_dict
        return percentiles_dict
        
    def desription_tofile(self, outfile):
        ''' 
        METHOD:        
        calculate basic statistics on 
        *** years, days, stations in record
        *** counts of NAN, Zero, drizzle, DWD intensity categories
        -----------------------------------------------------------------------
        INPUT:
        *** filename (use datasource, res, season)
        -----------------------------------------------------------------------
        OUTPUT:
        *** txt file with basic numbers and sttaistics
        -----------------------------------------------------------------------
        '''
   
        # write results to file
        with open(self.path3 + '/' + outfile + '_describe_dataset.txt', 'w') as f:
            f.write('DATAFRAME DESCRIPTION \nfilename: {}\n\n'.format(outfile))
            f.write('''Number of stations: {}\nTemporal resolution: {}\nResampled to: {}\nSeason (months, inclusive): {} to {}\n\n'''.format(self.nr_stations, self.resolution, self.resampling,
            self.season[0], self.season[1]))           
            f.write('''Lengths of Series [years]: \n''')
            [f.write('''{}: {} \n'''.format(key, np.round(value,2))) for key, value in self.years.items()]
            f.write('''\nOccurrences: \n''')
            [f.write('''{}: {} \n'''.format(key, value)) for key, value in self.occurrences.items()]
            f.write('''\n Occurrences over fixed threshold values: \n''')           
            [f.write('''{}: {} \n'''.format(key, value)) for key, value in self.occ_over_thres.items()]
            f.write('''\n\n''')
            f.write('''Percentile values and number of occurrences (of all observations in DataFrame > 0):\n''')
            for key, value in self.get_percentiles().items():
                f.write('''{}: \n'''.format(key))
                for key1, value1 in value.items():
                    [f.write('''{}: {}\n'''.format(key1, np.round(value1,2)))]
        
    def singlerecords_over_thres(self, threshold, outfile):
        ''' 
        METHOD:
        * Save dates of extreme records in the data exceeding a defined threshold.
        * Save figure of year, month, hour of events
        -----------------------------------------------------------------------
        INPUT:
        *** threshold: [mm] dates of periods with higher sums will be saved
        *** filename:  'str': name of file to be saved as csv and npy
        -----------------------------------------------------------------------
        OUTPUT:
        - destination directory is:
          r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Events_over_threshold'
        - returns dataframes of daily and hourly sums of all stations for the dates
          where at least one station exceeded the threshold
        - saves csv of dates, station ID and sums of highest station
        - transposed csv can be joined to a GIS station shapefile for visualization
        -----------------------------------------------------------------------
        '''

        csvname = outfile + '.csv'
        figname = outfile + '.png'
        print 'get events over threshold ...'
        dataframe_select = self.dataframe[self.dataframe > threshold].dropna(axis=0,
                                                                           how=
                                                                           'all')
        # datetime index of dataframe:
        idx = dataframe_select.index
        
        Dates = []
        Times = [] 
        # write csv file with date, daily sum, max hourly sum and max 10min intensity
        print 'Save dates of extreme precip intervals to csv ...'
        for [i, idx_i] in enumerate(idx):
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
            for [i, date_i] in enumerate(Dates):
                day = str(idx.year[i]) + '-' + str(idx.month[i]) + '-' + str(idx.day[i])
                df_day_xtr = self.dataframe[day]
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
     
        with open(self.path2 + '/Dates_' + csvname, 'wb') as f:
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
    
       
        day_tot_all.to_pickle(self.path2 + '/daily_sums_' + outfile + '.npy')
        hours_day_all.to_pickle(self.path2 + '/hourly_sums_' + outfile + '.npy')     
        
        # write precip sums of days to transposed csv file to be joined to .shp
        np.round(day_tot_all, 2).transpose().to_csv(self.path2 + '/DailySums_' +
                                                    csvname, na_rep=
                                                    0, index_label='synnr')
        np.round(hours_day_all, 2).transpose().to_csv(self.path2 + '/HourlySums_' +
                                                      csvname, na_rep=
                                                      0, index_label='synnr')
        print 'Saving daily and hourly sums of event to csv; '
        print 'formatted to be joined with station shape file in GIS'
        
        ''' Show peak times of maximum intensities
        temporal distributions of extremes of categories (min, h, d, 3d)
        over time (year, month, day, hour of the day)
        '''             
        
        dates = pd.DataFrame({'year':dataframe_select.index.year,
                              'month':dataframe_select.index.month,
                              'day':dataframe_select.index.day,
                              'hour':dataframe_select.index.hour,
                              'minute':dataframe_select.index.minute})
        

        # figure peak intensity times
        
        fig, [ax, ax1, ax0] = plt.subplots(3,  figsize=(6, 6))
        
        #fig.set_facecolor('#d3d3d3')
        
        ax0 = plt.subplot(211)
        dates.year.value_counts().sort_index().plot(kind='bar',
                                                    color='#ba55d3',
                                                    grid=False,
                                                    fontsize=7,
                                                    rot=45)
        ax0.set(xlabel='year') 
        
        ax1 = plt.subplot(223)
        dates.month.value_counts().sort_index().plot(kind='bar',
                                                     color='#da70d6',
                                                     grid=False,
                                                     fontsize=9,
                                                     rot=0)
        
        ticks = ['J', 'F', 'M',  'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        xlabels = ticks[self.season[0]-1: self.season[1]]
        ax1.set(xticklabels=xlabels, xlabel='month')
        
        
        ax2 = plt.subplot(224)
        dates.hour.value_counts().sort_index().plot(kind='bar',
                                                    color='#dda0dd',
                                                    grid=False,
                                                    fontsize=7,
                                                    rot=45)
        ax2.set(xlabel='hour')
          
        
        fig.suptitle("Records over " + str(threshold) + 'mm, season: ' + 
                     str(xlabels), fontsize=11)
        
        fig.savefig(self.path4 + '/' + figname, dpi=300)

    def EventDays(self, outfile, valid=0, wet_day_threshold=1):
        '''
        METHOD:
        * Filter sample by wet and dry days
        * start point wet day event: day > 2mm
        * end point: dry day (< 2mm)
        -----------------------------------------------------------------------
        INPUT:
        * valid: minimum number of valid records in one day to calculate a
          daily sum (depends on the resolution of class instance!)
          default=0
        * wet_day_threshold: [mm] - total sum a day must have (equal greater)
          to be defined wet. default: 1mm
        -----------------------------------------------------------------------
        OUTPUT:
        DataFrame with stationwise statistics (MultiIndex)
        * first day of event
        * length of event
        * total sum
        * mean rain rate [mm/d]
        * max daily rainfall
        -----------------------------------------------------------------------
        '''
        
        # resampling ensures that the timestamp of the datetime index is the same
        print "WARNING: 7-7am recordings will be assigned 0-24h"
        df_daily = resample_valid(self.rawinputdata, '1D', valid=valid, base=0) 
        # save a dataframe with the [mm] values
        df_values = resample_valid(self.rawinputdata, '1D', valid=valid, base=0) 
    
        
        # assign dry (0) and wet days (1) 
        df_daily[df_daily < wet_day_threshold] = 0  
        df_daily[df_daily >= wet_day_threshold] = 1
        
        print df_daily.head()
        # preallocate list where Event ID data will be stored
        #listall = [0] * len(df_daily.columns.values)
        #list_stats = [0] * len(df_daily.columns.values)
        Stats_Dict = {}
        
        # loop through all stations in the dataset
        for [loop, station] in enumerate(df_daily.columns.values):
            print 'Station processed: ', station
            # treat each station as series
            Series = df_daily[station]
 
            count = 0
            array_event = []
            # preallocate dict where the first day for each event is stored
            startday_dict = {}
            
            # loop through observations in each station series
            for [t, x] in enumerate(Series):
                # print 'step: ', t, ' value: ', x
                # if first observation is positive don't check for preceding day
                # assign event ID '1'
                if np.logical_and(t==0, x==1):
                    count = count+1
                    array_event.append(count)
                    startday = Series.index[t]
                    startday_dict.update({count : startday})
                    #print 'first day in record is wet! Event counter: ', count
                # if first observation is NaN, assign NaN
                elif np.logical_and(t==0, pd.isnull(Series[t])):
                        array_event.append(np.nan)            
                        #print 'first day missing value! Event counter: ', count
                        
                # if observation is either 1 or 0:
                else:
                    # if day is dry (='0') assign NaN for dry days
                    if x==0:
                        array_event.append(np.nan)
                        #print 'dry day', 'event counter: ', count
                    elif np.isnan(x):
                        array_event.append(np.nan)
                        #print 'no value day', 'event counter: ', count
                    # assign an event ID for wet days. Consecutive wet days get the
                    # same ID
                    else:
                        # assign the same event ID for consecutive wet days
                        if Series[t-1] == 1:
                            array_event.append(count)
                            #print 'consecutive wet day! Event counter: ', count
                        # assign new event ID if a dry day preceded the wet day
                        else:
                            count = count+1
                            array_event.append(count)
                            # save the date of the first day of event
                            startday = Series.index[t]
                            startday_dict.update({count : startday})
                            ##print 'wet day after dry or no value day! Event counter: ', count
            print count, ' events in station record', 'len array event', len(array_event)
            if count == 0:
                print 'station ', station, 'is null'
            '''for each station record add the event ID column, which attributes a
            number to events of consecutive wet days if at least one zero or NaN
            day is in between
            '''
            
            df = pd.DataFrame({station: df_values[station],
                               station + '_eventID': array_event})
                               
            
            
            # group by Events from 1 to x
            byEvent = df.groupby(station + '_eventID')
            # sum, average, max of observation within event
            stats = byEvent.agg([np.nansum, np.nanmean, len, max])
            
            stats.columns = stats.columns.get_level_values(1).drop_duplicates()           
            stats.columns = ['sum', 'mean rain rate', 'duration', 'max daily']
            
        
            # add column to dataframe: date of the first wet day and use as index
            stats['firstday'] =  startday_dict.values()       
            stats.index = stats.firstday
            
            # if no event in Station, add nans as peaks
            if stats.firstday.empty:
                stats1 = pd.DataFrame(columns=['peak 1', 'peak 2', 'peak 3',
                                               'perc nan', 'max h 1', 'max h 2'])
                stats = pd.concat([stats, stats1], axis=1)
                
            else:
                ''' 
                For each event in station record, use ORIGINAL DATAFRAME TO
                * calculate percentage of NaN during event
                * exctract peak intensities
                '''
                
                for [i, eachFirstDay], dur in zip(enumerate(stats.firstday), stats.duration):
                    # make scan range +1 so that last rec of scanning is the midnight 
                    # observaiton of the following day
                    scan_rng = pd.date_range(eachFirstDay, periods=dur+1, freq='D')
                    # get original raw data for the event span
                    ScanInterval = self.rawinputdata[station].ix[scan_rng[0]:scan_rng[-1]]
         
                    peaks = ScanInterval.order(ascending=False)[0:3]
                               
                    stats.loc[stats.firstday[i], 'peak 1'] = peaks.values[0]
                    stats.loc[stats.firstday[i], 'peak 2'] = peaks.values[1]
                    stats.loc[stats.firstday[i], 'peak 3'] = peaks.values[2]
                    
                    perc_nan = (1-(np.float(ScanInterval.count())/np.float(len(ScanInterval))))*100               
                    stats.loc[stats.firstday[i], 'perc nan'] = perc_nan
                   
                    mh = ScanInterval.resample('1H', how='sum').order(ascending=False)[0:3]              
                    stats.loc[stats.firstday[i], 'max h 1'] = mh.values[0]
                    stats.loc[stats.firstday[i], 'max h 2'] = mh.values[1]
                    
                    #------------------------------------------------------------------
            
            del stats['firstday']
            Stats_Dict.update({station: stats}) 
        
        #DayEventStatistics_all = pd.concat(list_stats, axis=1)
        
        DayStatistics_DataFrame = pd.concat(Stats_Dict, axis=1)
#        # add event ID for each Date
#        idxEvent = []
#        for x in range(len(DayStatistics_DataFrame)):
#            idxEvent = idxEvent.appen(x)
#        DayStatistics_DataFrame['ED'] = idxEvent
#        DayStatistics_DataFrame.set_index('ID', append=True, inplace=True)
        
        DayStatistics_DataFrame.to_pickle(self.path2 + '/'+ outfile + '_wet_day_event_statistics.npy')
        print 'Dataframe of Day Event Statistics saved to \n',  '/', outfile, '_wet_day_event_statistics.npy'       
        # save the dataframe of all stations and event IDs
        #DF_all = pd.concat(listall, axis=1)
        #DF_all.to_pickle(self.path2 + '/'+ outfile + '_wet_day_events.npy')
        
        return DayStatistics_DataFrame
        

    def EventHours(self, Dayframe, outfile, valid=0):
        ''' 
        METHOD:
        * Within the wet day events look for hourly resolved events
        * start point: hour > .19mm
        * end point: hour < .19mm (0r 2h?)
        -----------------------------------------------------------------------
        INPUT:
        * pd.DataFrame of wet days (all days with values will be scanned)
        * valid: number of required valid records in building hourly sums
          e.g., 10min data: 5 would mean 5/6; 5min data: 5 would mean 5/12
        -----------------------------------------------------------------------
        OUTPUT:
        * DataFrame with Events per station: 
        * - start point
        * - duration
        * - mean rain rate [mm/h]
        * - max h intensity [mm/h]
        * - peaks [mm/10 or 5min]
        -----------------------------------------------------------------------
        '''
        # yields for each day the longest duration (max()) of all stations
        
        # (works 2015-08-04):
        # Dayframe.iloc[:, Dayframe.columns.get_level_values(1)=='duration'].max(axis=1) 
        # yields the same: (works 2015-08-04):
        dur = Dayframe.xs('duration', level=1, axis=1).max(axis=1)   
        
        # ScanFrame: Dataframe of all wet days as found in EventDays
        ScanFrameList = []
        for day, dur in zip(dur.index, dur.values):
                   
            # make scan range +1 so that last rec of scanning is the midnight 
            # observaiton of the following day
            scan_rng = pd.date_range(day, periods=dur+1, freq='D')
            ScanInterval = self.rawinputdata.ix[scan_rng[0]:scan_rng[-1]]
#            ScanInterval = rawinputdata.ix[scan_rng[0]:scan_rng[-1]]
            ScanFrameList.append(ScanInterval)
        ScanFrame = pd.concat(ScanFrameList)
        print 'TEST 1 ScanFrame index duplicated?!: \n', ScanFrame.index.is_unique 
        idx = np.unique(ScanFrame.index, return_index=True)[1]
        ScanFrame = ScanFrame.iloc[idx]
        print 'TEST 2 ScanFrame index duplicated?!: \n', ScanFrame.index.is_unique  
        
        # resample the frame to get hourly sums
        df_hourly = resample_valid(ScanFrame, '1H', valid=valid)
        df_values = resample_valid(ScanFrame, '1H', valid=valid)
        
        # assign dry (0) and wet hours (1) 
        df_hourly[df_hourly < .2] = 0 
        df_hourly[df_hourly >= .2] = 1
        
       

        # preallocate dict where Event ID data will be stored
        Stats_Hourly_Dict = {}
        
        # loop through all stations in the dataset
        for [loop, station] in enumerate(df_hourly.columns.values):
            print 'station processed :', station
            # treat each station as series
            Series = df_hourly[station]

            count = 0
            array_event = []
            # preallocate dict where the start time for each event is stored
            starthour_dict = {}
            
            # loop through observations in each station series
            for [t, x] in enumerate(Series):
                # print 'step: ', t, ' value: ', x
                # if first observation is positive don't check for preceding hr
                # assign event ID '1'
                if np.logical_and(t==0, x==1):
                    count = count+1
                    array_event.append(count)
                    starthour = Series.index[t]
                    starthour_dict.update({count : starthour})
                    #print 'first hour in record is wet! Event counter: ', count
                # if first observation is NaN, assign NaN
                elif np.logical_and(t==0, pd.isnull(Series[t])):
                        array_event.append(np.nan)            
                        #print 'first hour missing value! Event counter: ', count
                        
                # if observation is either 1 or 0:
                else:
                    # if hour is dry (='0') assign NaN for dry hours
                    if x==0:
                        array_event.append(np.nan)
                        # print 'dry hour', 'event counter: ', count
                    elif np.isnan(x):
                        array_event.append(np.nan)
                        # print 'no value hour', 'event counter: ', count
                    # assign an event ID for wet hour. Consecutive wet hour get the
                    # same ID
                    else:
                        # assign the same event ID for consecutive wet hours
                        if Series[t-1] == 1:
                            array_event.append(count)
                            # print 'consecutive wet hour! Event counter: ', count
                        # assign new event ID if a dry hour preceded the wet hour
                        else:
                            count = count+1
                            array_event.append(count)
                            # save the date of the first hour of event
                            starthour = Series.index[t]
                            starthour_dict.update({count : starthour})
                            # print 'wet hour after dry or no value hour! Event counter: ', count
            print count, 'events detected'

            
            '''for each station record add the event ID column, which attributes a
            number to events of consecutive wet hours if at least one zero or NaN
            hour is in between
            '''
            df = pd.DataFrame({station: df_values[station],
                               station + '_eventID': array_event})
            
            # group by Events from 1 to x
            byEvent = df.groupby(station + '_eventID')
            # sum, average, max of observation within event
            stats = byEvent.agg([np.nansum, np.nanmean, len, max])
            
                      
            stats.columns = stats.columns.get_level_values(1).drop_duplicates()         
            stats.columns = ['sum', 'mean rain rate', 'duration', 'max hourly']

            # add column to dataframe: date of the first wet hour and use ans index
            stats['firsthour'] =  starthour_dict.values()       
            stats.index = stats.firsthour
            
            # if no event in Station, add nans instead of peaks
            if stats.firsthour.empty:
                stats1 = pd.DataFrame(columns=['peak 1', 'peak 2', 'peak 3',
                                               'perc nan'])
                stats = pd.concat([stats, stats1], axis=1)
            else:
                ''' 
                For each event in station record, use ORIGINAL DATAFRAME TO
                * calculate percentage of NaN during event
                * exctract peak intensities
                '''
                
                for [i, eachFirstHour], dur in zip(enumerate(stats.firsthour), stats.duration):
                    # make scan range +1 so that last rec of scanning is the first 
                    # observation of the following hour
                    scan_rng = pd.date_range(eachFirstHour, periods=dur+1, freq='H')
                    # get original raw data for the event span
                    ScanInterval = self.rawinputdata[station].ix[scan_rng[0]:scan_rng[-1]]
         
                    peaks = ScanInterval.order(ascending=False)[0:3]
                               
                    stats.loc[stats.firsthour[i], 'peak 1'] = peaks.values[0]
                    stats.loc[stats.firsthour[i], 'peak 2'] = peaks.values[1]
                    stats.loc[stats.firsthour[i], 'peak 3'] = peaks.values[2]
                    
                    perc_nan = (1-(np.float(ScanInterval.count())/np.float(len(ScanInterval))))*100               
                    stats.loc[stats.firsthour[i], 'perc nan'] = perc_nan
                    
                    #------------------------------------------------------------------
            del stats['firsthour']
            #print 'stats head\n\n', stats.head(20)
            Stats_Hourly_Dict.update({station: stats}) 
        
        #hourEventStatistics_all = pd.concat(list_stats, axis=1)
        
        hourStatistics_DataFrame = pd.concat(Stats_Hourly_Dict, axis=1)       
        hourStatistics_DataFrame.to_pickle(self.path2 + '/'+ outfile + '_wet_hour_event_statistics.npy')
        # save the dataframe of all stations and event IDs
        #DF_all = pd.concat(listall, axis=1)
        #DF_all.to_pickle(self.path2 + '/'+ outfile + '_wet_hour_events.npy')
        print 'Dataframe of Hour Event Statistics saved to /', outfile, '_wet_hour_event_statistics.npy'       
        
        return hourStatistics_DataFrame

def RSS(Dayframe):
    ''' 
    METHOD:
    * calculate ranked skill score of events in IndicatorFrame
    * rank each event based on indicators I(1)-I(n)
    * RSS(E) = sum of all ranks
    -----------------------------------------------------------------------
    INPUT:
    * Dataframe of event statistics (hourly or daily?)
    -----------------------------------------------------------------------
    OUTPUT:
    * table of individual ranks
    * list of RSS
    -----------------------------------------------------------------------
    '''
    
    ''' Each indicator of each station is ranked from 1-N (stationwise)
    for more than one value of the same size, they get the same rank, but the
    following gets the rank according to its position, not value. So if two
    max values are the same, the second highest value is the third highest
    observation and ranked '3'.
    '''
    rankdict = {}
    # ranks from high to low (highest gets '1', lowest 'N')
    rank_cols_hi = ['max daily', 'peak 1', 'peak 2', 'mean rain rate',
                    'max h 1']
    # ranks from low to high (lowest gets '1', highest 'N')
    rank_cols_lo = ['duration', 'perc nan']
                 
    for col in rank_cols_hi:         
        ranks = Dayframe.xs(col, level=1, axis=1).rank(method='min',
                                                        na_option='keep',
                                                        ascending=0)
        rankdict.update({col: ranks})   
                                             
    for col in rank_cols_lo:        
        ranks = Dayframe.xs(col, level=1, axis=1).rank(method='min',
                                                        na_option='keep',
                                                        ascending=1)        
        rankdict.update({col: ranks})   
        rankframe = pd.concat(rankdict, axis=1)
    
    
    ''' Ranked Skill Score Dataframe:
    '''
    RSS_dict = {}
    norm = len(rankframe.columns.get_level_values(0).drop_duplicates())
    for station in Dayframe.columns.get_level_values(0).drop_duplicates():
        RSS = (rankframe.xs(station, level=1, axis=1).sum(axis=1)/norm).rank(method='min',
                                                                    na_option='keep',
                                                                    ascending=1)
        RSS_dict.update({station: RSS})
        RSS_frame = pd.concat(RSS_dict, axis=1)
   
    return RSS_frame    
     
        
def flagging(self):
    ''' 
    METHOD:
    flag potential errors and threshold events?
    -----------------------------------------------------------------------
    INPUT:
    -----------------------------------------------------------------------
    OUTPUT:
    -----------------------------------------------------------------------
    '''
    
        
        
    '''
    does the peak intensity time vary from year to year?
   
    df = self.dataframe
    # return index of the maximum values for each station
    # station record
    max_dates_stations = dataframe.idxmax()       
        # gives for each date the station that had the highest value for the day
data.idxmax(axis=1)

# for each station the date where the station had its max
data.idxmax(axis=0) 

    # Values of max intensities per station
    pd_dates = pd.to_datetime(max_dates_stations.values)

    
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



   '''