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
    
    def __init__(self, dataframe, resolution='10min', season=[1, 12],
                 resampling=False):
        ''' class instance stationfiles (n=len(statnrs)*len(yrs))
        --------------------
        Class  attributes:
        --------------------
        dataframe: pd.DataFrame with DateTime Index
        resolution: temporal resolution of dataframe (frequency of pd.dataFrame)
                    default: '10min'
        resampling: resample Dataframe to other temporal resolution
                    default: False
                    options: '10min', '60Min', '1H', '24H' '1D', '3D'
        season: first and last month to be included in the DataFrame
        '''
        
        self.resolution = resolution
        self.resampling = resampling
        self.season = season 
        
        self.path1 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis'
        self.path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'
        self.path3 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description'
        self.path4 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description\Plots'
        
        month = dataframe.index.month
        selector = ((season[0] <= month) & (month <= season[1]))
        self.dataframe = dataframe[selector] 
               
        if resampling == False:
            print 'no resampling'
        else:
            print 'resampling dataframe to ', self.resampling
            self.dataframe = self.dataframe.resample(self.resampling, how='sum',
                                               closed='left', label='left',
                                               base=0).dropna(axis=0,
                                                              how='all')
                                                        
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
        
    def desription_tofile(self, outfile):
        ''' calculate basic statistics on 
        *** years, days, stations in record
        *** counts of NAN, Zero, drizzle, DWD intensity categories
        INPUT:
        *** filename (use datasource, res, season)
        OUTPUT:
        *** txt file with basic numbers and sttaistics
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



    def EventDataFrame(self):
        '''Generate dataframe with the events over the chosen threshold
        - get the Dates from events over threshold
        - extract the day of peak intensity plus minus 2 Days
        - run an running window of sums
            -> start of event: at least 3*10min > .2
            -> end of event: at least 1h of =< .1??
        '''
        
        
    def flagging(self):
        ''' flag potential errors and threshold events?
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