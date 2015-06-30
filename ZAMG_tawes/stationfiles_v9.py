### PYTHON MODULE FOR ZAMG TAWES STATION DATA
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 10:40:03 2015

@author: Kaddabadda, WEGC, FWF-DK CC
*** read raw data single files as downloaded from ZAMG tawes to Station Dataframe csv files
*** fill missing values with NAN
"""
import numpy as np
import pandas as pd
# import xray
import csv
import os
import numpy.ma as ma

''' SET PATHS DEPENDING ON CURRENT WORK STATION (Laptop or ksc)
'''
pth = str('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\Data_single_files2')
# pth = str('/media/katha/DOCUMENTS/WEGC/02_PhD_research/03_Data/ZAMG/Data_single_files')

'''paths for moving table file from source dir to destination dir'''
#src = "/media/katha/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes/stats_stats.csv"
#dst = "/media/katha/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Tables"
src = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\04_Programming\Python\Modules\ZAMG_tawes'
dst = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\04_Programming\Python\Tables'

'''Create a dictionary of synnr and station name from csv'''

with open(str(dst) + '\ZAMG_stations_SW_Alps_150216_noheader.csv') as stationcsvin:
    reader = csv.reader(stationcsvin)
    stat_dict = {rows[2]: rows[1] for rows in reader}
    stat_dict.pop('name', None)
    statlist = np.array(stat_dict.values())

### does the same as upper paragraph
#testlist = pd.read_csv(str(dst) + '\ZAMG_stations_SW_Alps_150216_noheader.csv',
#            usecols=[1,2], header=None, names=['synnr', 'name'], dtype='string')
#statlist1 = testlist['synnr'].tolist()
#namelist = testlist['name'].tolist()
#stat_dict1 = dict(zip(namelist, statlist1))


var_key = {0: 'date', 1: 'time', 2: 'temperature', 3: 'T_max', 4: 'T_min',
           5: 'rel_hum', 6: 'precip', 7: 'pressure', 8: 'dew_point_temp', 9:
           'wind_dir', 10: 'wind_strength'}


class Stationfile:
    '''Station data files read from ZAMG tawes2 with
    '''

    def __init__(self, statnr):
        ''' class instantiation stationfiles (n=len(statnrs)*len(yrs)) are
        instances of class Stationfile
        --------------------
        Class  attributes:
        --------------------
        var: column indices: 0=YYYMMDD, 1=HHMM, 2=tl, 3=tlmax, 4=tlmin,
        5=rf, 6=rfmax, 7=rfmin, 8=rr
        '''
        self.pth = pth
        self.stat_dict = stat_dict
        ''' Instance attributes:
        --------------------
        statnr: Number od station as in 'synnr' (!not 'statnr' in tawes2!)
        yr: Year of measurements
        '''
        self.statnr = statnr

    def start_record(self):
        '''Read in ZAMG station file data of the variable to read.
        1) Check the date and time of the first measurement and create a time
        array
        2) read the data and join with the time array
        '''
        years = np.array(range(1992, 2015))
        for i in range(len(years)):
            yr = years[i]
#            print 'Looking for first record year of station in year: ', yr
            if os.stat(str(self.pth) + '\zamg_tawes_station' + str(self.statnr)
                       + '_' + str(yr) + '.txt').st_size < 200:
#                print 'No tawes data in this file'
                pass
            else:
                # get date and time of first measurement in first year
                with open(str(self.pth) + '\zamg_tawes_station' +
                          str(self.statnr) + '_' + str(yr) + '.txt',
                          'r') as stationfile:
                    # begin time (because it might not be 00:10)
                    bt = int((np.genfromtxt(stationfile, delimiter=';',
                              skip_header=2, skip_footer=2,
                              usecols=(1), unpack=True))[0])
                    # convert start time from table to same format (eg.
                    # '10'= 00:10,'330' = 03:30, '1420' = 14:20)
                    if len(str(bt)) == 1:
                        starttime = '00:0' + str(bt)
                    elif len(str(bt)) == 2:
                        starttime = '00:' + str(bt)
                    elif len(str(bt)) == 3:
                        starttime = '0' + str(bt)[0] + ':' + str(bt)[1:3]
                    elif len(str(bt)) == 4:
                        starttime = str(bt)[0:2] + ':' + str(bt)[2:4]
                    else:
                        print 'error in creating startdate'
                    # begin date in first non-empty file since 1992
                with open(str(self.pth) + '\zamg_tawes_station' +
                          str(self.statnr) + '_' + str(yr) + '.txt',
                          'r') as stationfile:
                    bd_file = int((np.genfromtxt(stationfile,
                                   delimiter=';', skip_header=2,
                                   skip_footer=2, usecols=(0),
                                   unpack=True))[0])
                    # convert start date from table to same format (eg.
                    # '2030101' = 01/01/2003, '19990405' = 05/04/1999)
                    if len(str(bd_file)) == 6:  # years before 2000
                        startyear = '19' + str(bd_file)[0:2] + '/' +\
                                    str(bd_file)[2:4] + '/' + str(bd_file)[4:6]
                        print startyear
                    elif len(str(bd_file)) == 7:  # years afer 2000
                        startyear = '20' + str(bd_file)[1:3] + '/' +\
                            str(bd_file)[3:5] + '/' + str(bd_file)[5:7]
#                        print startyear
                    else:
                        print 'error in creating startyear'
                    # years of data availability (10'tawes) & stat nr
                    record = np.array(range(int(startyear[0:4]), 2015))
                    print 'years in record: ', str(len(record))
                    print 'first measurement', startyear, ' ', starttime
                break
        return startyear, starttime, record

    def read_raw(self, *vars):
        ''' Returns an array of 10 min raw tawes data of the selected
        station for the chosen variable over the entire record length.
        There are missing data (-99.) and there are missing lines
        (unknown missing data!)
        '''
        record = self.start_record()[2]

        for i in range(len(record)):
            yr = record[i]
#            print 'Reading data for year: ', yr
            with open(str(self.pth) + '\zamg_tawes_station' +
                      str(self.statnr) + '_' + str(yr) + '.txt', 'r')\
                    as stationfile:
                tawes_raw_single = np.genfromtxt(stationfile,
                                                 delimiter=';',
                                                 skip_header=2,
                                                 skip_footer=2,
                                                 usecols=(vars),
                                                 unpack=True)
                if i == 0:
                    result = tawes_raw_single
#                        print i
#                        print 'data points:', len(result)
                else:
                    result = np.append(result, tawes_raw_single)
#                        print i
#                        print 'number of data:', len(result)

        return result

    def end_record(self):
        ''' reads the date and time of the last measurement of a station record
        and creates a pandas date range array of the record period
        '''
        startyear = self.start_record()[0]
        starttime = self.start_record()[1]

        years = self.read_raw(0)
        times = self.read_raw(1)

        lastdate = int(years[-1])
        # convert start date from table to same format (eg.
        # '2030101' = 01/01/2003, '19990405' = 05/04/1999)
        if len(str(lastdate)) == 6:  # years before 2000
            enddate = '19' + str(lastdate)[0:2] + '/' + str(lastdate)[2:4] +\
                      '/' + str(lastdate)[4:6]
            print enddate
        elif len(str(lastdate)) == 7:  # years afer 2000
            enddate = '20' + str(lastdate)[1:3] + '/' + str(lastdate)[3:5] +\
                      '/' + str(lastdate)[5:7]
        else:
            print 'error in reading endyear'

        lasttime = int(times[-1])
        # convert end time from table to same format (eg.
        # '10'= 00:10,'330' = 03:30, '1420' = 14:20)
        if len(str(lasttime)) == 1:
            endtime = '00:0' + str(lasttime)
        elif len(str(lasttime)) == 2:
            endtime = '00:' + str(lasttime)
        elif len(str(lasttime)) == 3:
            endtime = '0' + str(lasttime)[0] + ':' + str(lasttime)[1:3]
        elif len(str(lasttime)) == 4:
            endtime = str(lasttime)[0:2] + ':' + str(lasttime)[2:4]
        else:
            print 'error in reading endtime'

        # last element years, last element times:
        end = enddate + ' ' + endtime
        start = startyear + ' ' + starttime
        print 'Station record from ', start, 'to ', end
        # create time array of actual length of the data series
        time_array_record = pd.date_range(start, end, freq='10min')

        # number of missing data not shown as missing data in the file
        missing_data_unknown = len(time_array_record) - len(times)

        return start, end, missing_data_unknown, time_array_record, times,\
            years

    def details_missing_values(self):
        ''' checks whether and how many data gaps exist in the station record
        and returns a list of the dates enclosing the detected data gaps
        '''
        mdu = self.end_record()[2]
        times = self.end_record()[4]
        years = self.end_record()[5]

        if mdu == 0:
            print 'dataset is complete'
            return

        else:
            print 'Missing lines detected: ', mdu
            detected_data_gaps = []
            diffs = []
            # differences between 10min measurements have to be 10, 50 or 2350
            # otherwise a data gap is detected
            for i in range(len(times)):
                diff = times[i-1]-times[i]
                diffs.append(diff)

            diffsp = np.array(diffs)
            # gives indices of inconsistent observation times
            indices = np.argwhere(np.logical_and(np.logical_and(diffsp != -10,
                                                                diffsp != -50),
                                                 diffsp != 2390))
            for i in range(len(indices)):
                check = indices[i]
                a = times[check-1:check+1]
                b = years[check-1:check+1]
                c = str(a) + ' ' + str(b)
                detected_data_gaps.append(c)

        return mdu, detected_data_gaps

    def record_fill(self, var):
        ''' find missing lines and fill with NaNs,
        returns a pandas time series of 10Min frequency for the length of the
        station record
        '''
        data = self.read_raw(var)
        years = self.read_raw(0)
        times = self.read_raw(1)
        time_array_record = self.end_record()[3]

        index = np.zeros(len(years), dtype=pd.datetime)
        # put a time stamp on each observation based on date and time in .csv
        for i in range(len(years)):
            date = int(years[i])
            # print date
            if len(str(date)) == 6:  # years before 2000
                yr = int('19' + str(date)[0:2])
                mo = int(str(date)[2:4])
                d = int(str(date)[4:6])

            elif len(str(date)) == 7:  # years afer 2000
                yr = int('20' + str(date)[1:3])
                mo = int(str(date)[3:5])
                d = int(str(date)[5:7])
            else:
                print 'error in creating index year'
                break

            time = int(times[i])
#            print time
            if len(str(time)) == 1:
                h = 00
                mi = int('0' + str(time))
            elif len(str(time)) == 2:
                h = 00
                mi = time
            elif len(str(time)) == 3:
                h = int('0' + str(time)[0])
                mi = int(str(time)[1:3])
            elif len(str(time)) == 4:
                h = int(str(time)[0:2])
                mi = int(str(time)[2:4])
            else:
                print 'error in creating index time'

            ''' Midnight observation index jumps from 'day-X 0' to 'day-X -1
            2400' for some station mid-record. '24' is not supported in pd,
            so 2400 of day X-1 are dated forward to NEXT day X, 00:00
            '''
            if h == 24:
                h = 00
                date = int(years[i+1])
                # print date
                if len(str(date)) == 6:  # years before 2000
                    yr = int('19' + str(date)[0:2])
                    mo = int(str(date)[2:4])
                    d = int(str(date)[4:6])

                elif len(str(date)) == 7:  # years afer 2000
                    yr = int('20' + str(date)[1:3])
                    mo = int(str(date)[3:5])
                    d = int(str(date)[5:7])
                else:
                    print 'error in creating index year'
                    break

            dt = pd.datetime(yr, mo, d, h, mi)
#            print dt
            index[i] = dt
        # make a pandas time series with the data and created time stamps
        # data gaps are in this time series
        # namets = str(var_key.values()[var])
        ts = pd.Series(data, index, name=str(var_key.values()[var]))
#        print 'stil here'
#        print 'length time series data raw', len(ts)
#        print 'length index', len(index), type(index)
#        print 'length time series created from start end date', len(time_array_record)
        # reindex data-gap time series with time series that covers the range
        # from first to last observation
        ts_nan = ts.reindex(time_array_record)

        return ts_nan

    def statDataFrame(self):
        ''' creates a pandas Dataframe for the station object,
        consistent date_time stamps and tawes missing values converted to NaN
        correcter to true values [mm, centigrade]
        '''
        ts_list = []
        for i in range(2,11):
            ts = self.record_fill(i)
            ts_list.append(ts)

        df = pd.concat([ts_list[0], ts_list[1], ts_list[2],
                   ts_list[3],ts_list[4], ts_list[5], ts_list[6],
                   ts_list[7],ts_list[8]], axis=1)

        # replace '-99' NaNs with nan
        df = df.replace([-999, -99], [np.nan, np.nan])
        # df = df.replace(-99, np.nan)
        # correct to real values tawes: T 1/10centigrade, precip: 1/10mm
        f2 = lambda x: x/10
        df.precip = df['precip'].apply(f2)
        df.temperature = df['temperature'].apply(f2)
        df.T_max = df['T_max'].apply(f2)
        df.T_min = df['T_min'].apply(f2)
        df.wind_strength = df['wind_strength'].apply(f2)
        df.dew_point_temp = df['dew_point_temp'].apply(f2)
        df.pressure = df['pressure'].apply(f2)
        # this code return a new frame without rel_hum
        # df = df[['precip', 'temperature', 'T_min', 'T_max']].apply(f2)
        return df


# plots of not null statistics
# event detection routine
# daily and 24 hr sums
#        # only use extended summer season
#        df_summer = df.ix['2014/05':'2014/09']
#        # precipitation for Aril 2 2012
#        df_summer_precip = df['precip'].ix['2012/07/04']


