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


class StationDataFrame:
    ''' 
    ------------------------------------------------
    Methods to analyse observed station net datasets and identify extremes
    ------------------------------------------------
    
    Instance = Events(pd.DataFrame)
    
    '''  
    
    def __init__(self, dataframe, resolution=0, season=[1, 12]):
        ''' class instance stationfiles (n=len(statnrs)*len(yrs))
        --------------------
        Class  attributes:
        --------------------
        dataframe: pd.DataFrame with DateTime Index
        resolution: resample temporal resolution
                    default: no resampling (0)
                    options: '10min', '60Min', '1H', '24H' '1D', '3D'
        season: first and last month to be included in the DataFrame
        '''
        
        self.resolution = resolution 
        self.season = season 
        
        self.path1 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis'
        self.path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'
        self.path3 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description'
        self.path4 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description\Plots'
        
        month = dataframe.index.month
        selector = ((season[0] <= month) & (month <= season[1]))
        self.dataframe = dataframe[selector] 
               
        if resolution == 0:
            print 'no resampling'
            pass
        else:
            print 'resampling dataframe to ', self.resolution
            self.dataframe = self.dataframe.resample(self.resolution, how='sum',
                                               closed='left', label='left',
                                               base=0).dropna(axis=0,
                                                              how='all')
    

    
        # Thresholds selectors: boolean matrices returning selection              
        self.thres_sel = {'fixed': {'5min' : {'heavy Wussow': self.dataframe>=5,
                                              'heavy Schimpf': self.dataframe>=7.5,
                                              'heavy DWD': self.dataframe>=5},
                                    '10min' : {'drizzle': self.dataframe==.1,
                                               'light': (self.dataframe>.1) &
                                                   (self.dataframe<.5),
                                               'moderate': (self.dataframe>= .5) &
                                                      (self.dataframe<1.7),
                                               'heavy': (self.dataframe>=1.7) &
                                                   (self.dataframe<8.3),
                                               'very heavy': self.dataframe>=8.3,
                                               'torrential': self.dataframe>17},
                                    '1H': {'drizzle': (self.dataframe>.1) &
                                                 (self.dataframe<.5),
                                           'light': (self.dataframe>=.5) &
                                               (self.dataframe<2.5),
                                            'moderate:': (self.dataframe>=2.5) &
                                                    (self.dataframe<10),
                                            'heavy': self.dataframe>=10,
                                            'very heavy': self.dataframe>=50},
                                    '1D' : {'Schimpf': self.dataframe>=35,
                                            'Wussow': self.dataframe>=84.9},
                                    '3D' : {'Carinthian': self.dataframe>=177},
                         'percentile': {'p99' : [self.get_percentiles()['p99']
                                               ['value']],
                                        'p99.9' : [self.get_percentiles()['p99']
                                                 ['value']]},
                         'stats': {'zeros': self.dataframe==0,
                                   'NaN': pd.isnull(self.dataframe)}}    
    
    
    
    def properties(self):
        if self.resolution == 0:
            print 'Temporal resolution: original dataframe \n'
        else:
            print 'Temporal resolution: ', self.resolution, '(resampled)\n'
        print 'Season (months): ', self.season[0], ' to ', self.season[1] 
    
    def get_percentiles(self):
        ''' calculate percentiles all data in frame (all stations, all times)
        *** output: [p95, p98, p99, p99.9]
        *** !!! ignores zeros !!!
        *** and number of occurrences over percentile
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
        
    def events_over_threshold(self, threshold, outfile):
        ''' Save dates of extreme events exceeding a defined threshold.
        
        INPUT:
        *** threshold: [mm] dates of periods with higher sums will be saved
        *** filename:  'str': name of file to be saved as csv and npy

        
        OUTPUT:
        - destination directory is:
          r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Events_over_threshold'
        - returns dataframes of daily and hourly sums of all stations for the dates
          where at least one station exceeded the threshold
        - saves csv of dates, station ID and sums of highest station
        - transposed csv can be joined to a GIS station shapefile for visualization
        '''

        csvname = outfile + '.csv'
       
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
        
        # return day_tot_all, hours_day_all   

    def intensity_occurrences(self, resolution):
        ''' returns the numbers of occurrences of events over thresholds
        INPUT:
        *** resolution '5min, '10min', '1D', '
        '''
        
        # count the instances fulfilling each selection criterion
        for key in self.thres_sel.keys():      
            for subkey in self.thres_sel[key].keys():                       
                if key == 'fixed':                    
                    for subsubkey in self.thres_sel[key][resolution].keys():
                        nr = self.dataframe[self.thres_sel[key][subkey][subsubkey]].count(0).sum()
                        print key, resolution, subsubkey, ':  ', nr 
                else:
                    nr = self.dataframe[self.thres_sel[key][subkey]].count(0).sum()
                    print key, subkey, ':  ', nr 
    
    
    def describe_dataset(self, outfile):
        ''' calculate basic statistics on 
        *** years, days, stations in record
        *** counts of NAN, Zero, drizzle, DWD intensity categories
        INPUT:
        *** pandas dataframe
        *** temporal resolution of df (thresholds depend on time steps)
        OUTPUT:
        *** table of statistics and numbers of dataframe
        '''
        
        df = self.dataframe
        df_statistics = df.describe(percentiles=[.5, .9, .999])
        
        ncols = len(self.dataframe.columns)
        print 'Number of stations: ', ncols        
                
        records = []
        for eachCol in self.dataframe.columns:
            series = self.dataframe[eachCol].dropna()
            rec_len = len(range(series.index.year[0], series.index.year[-1]+1))
            records.append(rec_len)
        records = np.hstack(records)
        
        years = {'longest':[records.max()], 
                 'shortest':[records.min()],
                 'mean': [records.mean()],
                 'median':[np.median(records)],
                 'cumulative':[records.sum()]}
              

                
                
        
        
        
        
                                 
        
'''        
        total = df[Threshold_Selectors[key1][key2][key3]].count(0).sum()
    
        total_incl_zero = df.count(0).sum()
        total_excl_zero = df[df>0].count(0).sum()
        total_zero = df[df==0].count(0).sum()    
        
       
        
        days = selected.resample('D', how='sum', closed='left', label='left').dropna()    
        nr_days_in_selection = np.size(days)
        # percentage of observations fulfilling selection
        percent_selection = np.round(np.float(np.size(selected))/np.float(np.size(df))*100, 2)   
        
        for i in thresholds.values[res]:
            
            occurrence_days = selected.resample('D', how='sum', closed='left',
                                                label='left').dropna()
            nr_days_with_P = np.size(occurrence_days)
            
            percent_selected = np.round(np.float(np.size(selected))/
                                        np.float(np.size(df))*100, 2)
            
    
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
    
    
    def temporal_distribution(self, percentile):
        get temporal distributions of extremes of categories (min, h, d, 3d)
        over time (year, month, day, hour of the day)
        
        df = self.dataframe
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
    data.idxmax(axis=0)   '''