# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:19:03 2015
edited 2015 07 13
@author: Kaddabadda

VERSION for ZAMG 10min data and using the ZAMG daily dataset (ZAMG 'tag' table
in sybase) for the Tmax temperatures on the event day and the day preceding
the event. 

This should be outdated when the new file EventFrameClass.py is finished for
* both AHYD 5min and ZAMG 10min high res data
* using Spartacus as Tmax reference for all stations

-------------------------------------------------------------------------------
CLASS EVENTFRAMES
-------------------------------------------------------------------------------
Methods to analyse observed station net datasets and identify extremes

* resample function with NaN option
* Eventframes with methods:
  - get_percentiles
  - desription_tofile
  - singlerecords_over_thres
  - EventDays
  - EventHours


"""
import numpy as np
import pandas as pd


def resample_valid(df, res, valid=0, **kwargs):    
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
    df1 = df.resample(res, how=[np.sum, pd.Series.count], closed='left',
                     label='left', **kwargs)
    '''drop all rows where the count of valids is smaller than accepted'''
    querystr = 'count >= ' + str(valid)  
    '''df2 where Series has equal or more valid observations as queried: '''
    df2 = df1.query(querystr)
    if df2.empty:
        '''if there is no accepted observation:
        substitute all with np.nan'''
        df1['sum'] = np.nan
        Series = df1['sum']
    else:
        '''otherwise: take the valid sums and substitute the invalid with
        np.nan'''
        Series = df2['sum']
        '''resampling re-inserts NaN for dropped rows and rename column'''
        Series = Series.resample(res)    
    return Series


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
        * dataframe: pd.Series with DateTime Index      
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
        self.station = dataframe.name
        
        '''KADDABADDA-PC PATHS'''
#        ZAMG_daily_Tmax = pd.read_pickle(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\DAILY\ZAMG_daily_Tmax_1992-2004.npy')
#        self.ZAMG_tag = ZAMG_daily_Tmax
        '''SPARTACUS TASMAX'''
        SPARTA_tasmax = pd.read_pickle(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\StationTasmaxIDW\StationSeries\IDW_tasmax_ALLstations.npy')
        SPARTA_tasmax.index = SPARTA_tasmax.index.normalize()        
        self.sparta = SPARTA_tasmax 
        
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
             
        # numbers on the lengths of the series of the stations
        series = self.dataframe.dropna()
        if series.empty:
            rec_len = np.nan
        else:
           rec_len = len(range(series.index.year[0], series.index.year[-1]+1))
        print 'record length: ', rec_len, ' years'
        
    def get_percentiles(self, how='wet'):
        ''' 
        METHOD:
        * calculate percentiles all data in frame (all stations, all times)
        * !!! ignores zeros !!!
        -----------------------------------------------------------------------
        INPUT:
        * DataFrame instance of class
        * method: 'wet': only considers wet record
                  'dry': calculation based on all valid vals incl. zero
        -----------------------------------------------------------------------
        OUTPUT:
        * [p95, p98, p99, p99.9]
        * and number of occurrences over percentile
        -----------------------------------------------------------------------
        '''

        tet = self.dataframe.values
        if how == 'wet':
            tet[tet==0] = np.nan
        else:    
            pass    
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

#        print 'get events over threshold ...'
#        dataframe_select = self.dataframe[self.dataframe > threshold].dropna(axis=0,
#                                                                           how=
#                                                                           'all')


    def EventDays(self, outfile, valid=0, wet_day_threshold=1):
        '''
        METHOD:
        * Filter sample by wet and dry days
        * start point wet day event: day > threshold [mm]
        * end point: dry day (< threshold [mm])
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
        
        ''' resampling ensures that the timestamp of the datetime index is 
        the same'''
        print "WARNING: 7-7am recordings will be assigned 0-24h"
        df_daily = resample_valid(self.rawinputdata, '1D', valid=valid, base=0) 
        ''' save a dataframe with the [mm] values '''
        df_values = resample_valid(self.rawinputdata, '1D', valid=valid, base=0) 
    
        ''' assign dry (0) and wet days (1) ''' 
        df_daily[df_daily < wet_day_threshold] = 0  
        df_daily[df_daily >= wet_day_threshold] = 1
        
        Series = df_daily
        ''' counter goes up with each event'''
        count = 0
        array_event = []
        ''' preallocate dict where the first day for each event is stored '''
        startday_dict = {}
        ''' loop through observations in each station series '''
        for [t, x] in enumerate(Series):
            # print 'step: ', t, ' value: ', x
            if np.logical_and(t==0, x==1):
                '''if first observation is positive don't check for preceding day
                and assign event ID '1' '''
                count = count+1
                array_event.append(count)
                startday = Series.index[t]
                startday_dict.update({count : startday})
            elif np.logical_and(t==0, pd.isnull(Series[t])):
                ''' if first observation is NaN, assign NaN'''
                array_event.append(np.nan)            
            else:
                ''' if observation is either 1 or 0:
                if day is dry (='0') assign NaN for dry days'''
                if x==0:
                    array_event.append(np.nan)
                    #print 'dry day', 'event counter: ', count
                elif np.isnan(x):
                    array_event.append(np.nan)
                    #print 'no value day', 'event counter: ', count
                    ''' assign an event ID for wet days. Consecutive wet days get the
                    same ID '''
                else:
                    ''' assign the same event ID for consecutive wet days '''
                    if Series[t-1] == 1:
                        array_event.append(count)
                        #print 'consecutive wet day! Event counter: ', count
                    else:
                        ''' assign new event ID if a dry day preceded the wet day '''
                        count = count+1
                        array_event.append(count)
                        ''' save the date of the first day of event'''
                        startday = Series.index[t]
                        startday_dict.update({count : startday})
                        ##print 'wet day after dry or no value day! Event counter: ', count
        print count, ' events in station record'

            
        '''for each station record add the event ID column, which attributes a
        number to events of consecutive wet days if at least one zero or NaN
        day is in between
        '''
        df = pd.DataFrame({self.station: df_values,
                           self.station + '_eventID': array_event})                     
        ''' group by Events from 1 to x'''
        byEvent = df.groupby(self.station + '_eventID')
        ''' sum, average, max of observation within event'''
        stats = byEvent.agg([np.nansum, np.nanmean, len, max])
        stats.columns = stats.columns.get_level_values(1).drop_duplicates()           
        stats.columns = ['sum', 'mean rain rate', 'duration', 'max daily']
        ''' add column to dataframe: date of the first wet day and use as index
        '''
        stats['firstday'] =  startday_dict.values()       
        stats.index = stats.firstday 
        ''' if no event in Station, add nans as peaks'''
        if stats.firstday.empty:
            stats1 = pd.DataFrame(columns=['peak 1', 'peak 2', 'peak 3',
                                           'perc nan', 'max h 1', 'max h 2', 
                                           'Tmax_b', 'Tmax_a'])
            stats = pd.concat([stats, stats1], axis=1)
            
        else:
            ''' 
            For each event in station record, use ORIGINAL DATAFRAME TO
            * calculate percentage of NaN during event
            * exctract peak intensities
            '''
            
            for [i, eachFirstDay], dur in zip(enumerate(stats.firstday), stats.duration):
                '''make scan range +1 so that last rec of scanning is the midnight 
                observaiton of the following day'''
                scan_rng = pd.date_range(eachFirstDay, periods=dur+1, freq='D')
                '''get original raw data for the event span'''
                ScanInterval = self.rawinputdata.ix[scan_rng[0]:scan_rng[-1]]
     
                peaks = ScanInterval.order(ascending=False)[0:3]
                           
                stats.loc[stats.firstday[i], 'peak 1'] = peaks.values[0]
                stats.loc[stats.firstday[i], 'peak 2'] = peaks.values[1]
                stats.loc[stats.firstday[i], 'peak 3'] = peaks.values[2]
                
                perc_nan = (1-(np.float(ScanInterval.count())/np.float(len(ScanInterval))))*100               
                stats.loc[stats.firstday[i], 'perc nan'] = perc_nan
                ''' get max hour sum'''
                mh = ScanInterval.resample('1H', how='sum').order(ascending=False)[0:3]              
                stats.loc[stats.firstday[i], 'max h 1'] = mh.values[0]
                stats.loc[stats.firstday[i], 'max h 2'] = mh.values[1]
                '''add ZAMG Tmax of the onset day and the day prior to onset day'''
#                stats.loc[stats.firstday[i], 'Tmax_b'] = self.ZAMG_tag[station].loc[stats.firstday[i]]
                stats.loc[stats.firstday[i], 'Tmax_b'] = self.sparta[int(self.station)].loc[stats.firstday[i]]
                # print 'stats.firstday[i]: ', stats.firstday[i]
                '''get location of Tmax preceding the onset day'''
#                loc_prec = (self.ZAMG_tag[station].index.get_loc(stats.firstday[i]))-1
                loc_prec = (self.sparta[int(self.station)].index.get_loc(stats.firstday[i]))-1
#                stats.loc[stats.firstday[i], 'Tmax_a'] = self.ZAMG_tag[station][loc_prec]
                stats.loc[stats.firstday[i], 'Tmax_a'] = self.sparta[int(self.station)][loc_prec]
                
                #------------------------------------------------------------------
        
        del stats['firstday']
        return stats
      

    def EventHours(self, Dayframe, outfile, wet_hour_threshold=.2, valid=0):
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
        * wet_hour_threshold: only hourly sums equal and greater will be
          considered
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
        ''' ScanFrame: Dataframe of all wet days as found in EventDays '''
        ScanFrameList = []
        ''' timedelta to start hour event scan one day before the first wet day.
        This way, onset on the previous day is not ruled out'''
        from datetime import timedelta
        one_day = timedelta(days=1)
        
        for day, dur in zip(Dayframe.index, Dayframe.duration):
            ''' scan all wet days +- 1 for wet hours'''
            '''take the onset days and duration from day events'''
            scan_rng = pd.date_range(day-one_day, periods=dur+1, freq='D')
            ''' cut out the data from the original data'''
            ScanInterval = self.rawinputdata.ix[scan_rng[0]:scan_rng[-1]]
            ScanFrameList.append(ScanInterval)
        '''put all original wet day observations in one frame'''    
        ScanFrame = pd.concat(ScanFrameList)
        '''test whether a day has entered the scan frame twice and correct'''
        print 'TEST for duplicates in index...'
        if ScanFrame.index.is_unique is True:
            print 'no duplicates in index'
            pass
        else:
            idx = np.unique(ScanFrame.index, return_index=True)[1]
            ScanFrame = ScanFrame.iloc[idx]
            print 'TEST 2 ScanFrame index duplicated?!: \n', ScanFrame.index.is_unique  
        '''resample the frame to get hourly sums'''
        df_hourly = resample_valid(ScanFrame, '1H', valid=valid)
        df_values = resample_valid(ScanFrame, '1H', valid=valid)
        '''assign dry (0) and wet hours (1) '''
        df_hourly[df_hourly < wet_hour_threshold] = 0 
        df_hourly[df_hourly >= wet_hour_threshold] = 1
        count = 0
        array_event = []
        ''' preallocate dict where the start time for each event is stored'''
        starthour_dict = {}
        # loop through observations in station series
        for t, x in enumerate(df_hourly):
#            print 'step: ', t, ' value: ', x
            if np.logical_and(t==0, x==1):
                '''if first observation is positive don't check for preceding hr
                assign event ID'''
                count = count+1
                array_event.append(count)
                starthour = df_hourly.index[t]
                starthour_dict.update({count : starthour})
#                print 'first hour in record is wet! Event counter: ', count
                ''' if first observation is NaN, assign NaN'''
            elif np.logical_and(t==0, pd.isnull(df_hourly[t])):
                    array_event.append(np.nan)            
#                    print 'first hour missing value! Event counter: ', count  
                    ''' if observation is either 1 or 0:'''
            else:
                # if hour is dry (='0') assign NaN for dry hours
                if x==0:
                    array_event.append(np.nan)
#                    print 'dry hour', 'event counter: ', count
                elif np.isnan(x):
                    array_event.append(np.nan)
#                    print 'no value hour', 'event counter: ', count
                # assign an event ID for wet hour. Consecutive wet hour get the
                # same ID
                else:
                    # assign the same event ID for consecutive wet hours
                    if df_hourly[t-1] == 1:
                        array_event.append(count)
#                        print 'consecutive wet hour! Event counter: ', count
                    # assign new event ID if a dry hour preceded the wet hour
                    else:
                        count = count+1
                        array_event.append(count)
                        # save the date of the first hour of event
                        starthour = df_hourly.index[t]
                        starthour_dict.update({count : starthour})
#                        print 'wet hour after dry or no value hour! Event counter: ', count
        print count, 'events detected'
        '''for each station record add the event ID column, which attributes a
        number to events of consecutive wet hours if at least one zero or NaN
        hour is in between
        '''
        df = pd.DataFrame({self.station: df_values,
                           self.station + '_eventID': array_event})
        # group by Events from 1 to x
        byEvent = df.groupby(self.station + '_eventID')
        # sum, average, max of observation within event
        stats = byEvent.agg([np.nansum, np.nanmean, len, max])                             
        stats.columns = stats.columns.get_level_values(1).drop_duplicates()         
        stats.columns = ['sum', 'mean rain rate', 'duration', 'max hourly']
        ''' add column to dataframe: date of the first wet hour and
            use as index'''
        stats['firsthour'] =  starthour_dict.values()       
        stats.index = stats.firsthour       
        # if no event in df_hourly Series, add nans instead of values
        if stats.firsthour.empty:
            stats1 = pd.DataFrame(columns=['peak 1', 'peak 2', 'peak 3',
                                           'perc nan', 'Tmax_b', 'Tmax_a'])
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
                ScanInterval = self.rawinputdata.ix[scan_rng[0]:scan_rng[-1]]
     
                peaks = ScanInterval.order(ascending=False)[0:3]
                           
                stats.loc[stats.firsthour[i], 'peak 1'] = peaks.values[0]
                stats.loc[stats.firsthour[i], 'peak 2'] = peaks.values[1]
                stats.loc[stats.firsthour[i], 'peak 3'] = peaks.values[2]
                
                perc_nan = (1-(np.float(ScanInterval.count())/np.float(len(ScanInterval))))*100               
                stats.loc[stats.firsthour[i], 'perc nan'] = perc_nan
                
                # add ZAMG Tmax of the onset day and the day prior to onset day
                # only use day, reset onset hour to 00:00:00
                day = pd.DatetimeIndex([stats.firsthour[i]]).normalize()[0]
               # print 'day:  ', day
                stats.loc[stats.firsthour[i], 'Tmax_b'] = self.sparta[int(self.station)].loc[day]
                #get location of Tmax preceding the onset day
                loc_prec = (self.sparta[int(self.station)].index.get_loc(day))-1
               # print 'loc_prec:', loc_prec, 'type: ', type(loc_prec)
                stats.loc[stats.firsthour[i], 'Tmax_a'] = self.sparta[int(self.station)][loc_prec]
                ''' # add ZAMG Tmax of the onset day and the day prior to onset day
                stats.loc[stats.firstday[i], 'Tmax_b'] = self.ZAMG_tag[station].loc[stats.firstday[i]]
                print 'stats.firstday[i]: ', stats.firstday[i]
                #get location of Tmax preceding the onset day
                loc_prec = (self.ZAMG_tag[station].index.get_loc(stats.firstday[i]))-1
                stats.loc[stats.firstday[i], 'Tmax_a'] = self.ZAMG_tag[station][loc_prec]'''   
   
                #------------------------------------------------------------------
        del stats['firsthour']
        return stats
    
#    def RSS(Dayframe):
#        ''' 
#        METHOD:
#        * calculate ranked skill score of events in IndicatorFrame
#        * rank each event based on indicators I(1)-I(n)
#        * RSS(E) = sum of all ranks
#        -----------------------------------------------------------------------
#        INPUT:
#        * Dataframe of event statistics (hourly or daily?)
#        -----------------------------------------------------------------------
#        OUTPUT:
#        * table of individual ranks
#        * list of RSS
#        -----------------------------------------------------------------------
#        '''
#        
#        ''' Each indicator of each station is ranked from 1-N (stationwise)
#        for more than one value of the same size, they get the same rank, but the
#        following gets the rank according to its position, not value. So if two
#        max values are the same, the second highest value is the third highest
#        observation and ranked '3'.
#        '''
#        rankdict = {}
#        # ranks from high to low (highest gets '1', lowest 'N')
#        rank_cols_hi = ['max daily', 'peak 1', 'peak 2', 'mean rain rate',
#                        'max h 1']
#        # ranks from low to high (lowest gets '1', highest 'N')
#        rank_cols_lo = ['duration', 'perc nan']
#                     
#        for col in rank_cols_hi:         
#            ranks = Dayframe.xs(col, level=1, axis=1).rank(method='min',
#                                                            na_option='keep',
#                                                            ascending=0)
#            rankdict.update({col: ranks})   
#                                                 
#        for col in rank_cols_lo:        
#            ranks = Dayframe.xs(col, level=1, axis=1).rank(method='min',
#                                                            na_option='keep',
#                                                            ascending=1)        
#            rankdict.update({col: ranks})   
#            rankframe = pd.concat(rankdict, axis=1)
#        
#        
#        ''' Ranked Skill Score Dataframe:
#        '''
#        RSS_dict = {}
#        norm = len(rankframe.columns.get_level_values(0).drop_duplicates())
#        for station in Dayframe.columns.get_level_values(0).drop_duplicates():
#            RSS = (rankframe.xs(station, level=1, axis=1).sum(axis=1)/norm).rank(method='min',
#                                                                        na_option='keep',
#                                                                        ascending=1)
#            RSS_dict.update({station: RSS})
#            RSS_frame = pd.concat(RSS_dict, axis=1)
#       
#        return RSS_frame    
#         
#            
#    def flagging(self):
#        ''' 
#        METHOD:
#        flag potential errors and threshold events?
#        -----------------------------------------------------------------------
#        INPUT:
#        -----------------------------------------------------------------------
#        OUTPUT:
#        -----------------------------------------------------------------------
#        '''
#        
#            
#            
#        '''
#        does the peak intensity time vary from year to year?
#       
#        df = self.dataframe
#        # return index of the maximum values for each station
#        # station record
#        max_dates_stations = dataframe.idxmax()       
#            # gives for each date the station that had the highest value for the day
#    data.idxmax(axis=1)
#    
#    # for each station the date where the station had its max
#    data.idxmax(axis=0) 
#    
#        # Values of max intensities per station
#        pd_dates = pd.to_datetime(max_dates_stations.values)
#    
#        
#        # days at which more than one station had its maximum
#        # normalize index for min and h data?
#        dup_dates = dates[dates.duplicated()]
#        # which dates occur how often?
#        dates.value_counts()
#
#
#
## dates over 99th percentile
#
#  
#    
#dataframe.describe()
## how many valid records per station:
#dataframe.count(0)
## how many valid records per date
#dataframe.count(1)
#
#
#
#   '''