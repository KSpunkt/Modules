# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:16:37 2015

@author: Kaddabadda
Reads daily precipitation sums from N-Tagessummenfiles from AHYD into one dataframe
"""
import pandas as pd
import numpy as np
import csv as csv
import locale
pth = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\Tagessummen'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'

emptylist = []
# erroneous_files = []
'''Create a dictionary of synnr and station name from csv'''

with open(str(src) + '\Stationen_AHYD_DailySumData_noheader.csv') as stationcsvin:
    reader = csv.reader(stationcsvin)
    stat_dict = {rows[2]: rows[1] for rows in reader}
    stat_dict.pop('name', None)
    statlist_AHYD = np.array(stat_dict.values())


for eachStatNr in statlist_AHYD:
    print 'processing station nr: ', eachStatNr
    #eachStatNr = statlist_AHYD[1]
    '''each station csv has diffent number of header lines, thus try
    different numbers  until no Error Message is raised
    '''
    skip=20
    while True:
        try:
            print 'skipping ', skip, 'lines in header'
            ha = pd.read_csv(str(pth) + '\N-Tagessummen-' + eachStatNr + '.csv',
                             sep=';', skipinitialspace=True, header=None,
                             skiprows=skip, index_col=0, parse_dates=True,
                             dayfirst=True, names=['date',str(eachStatNr)],
                             skipfooter=1, engine='python')

            # ha[str(eachStatNr)] = ha[str(eachStatNr)].apply(lambda x: x.replace(",",".")).astype(float)
            ha[eachStatNr] = ha[eachStatNr].apply(lambda x: x.replace(",",".")).astype(float)
            # replace missing values with NaN
            selector = ha<0
            ha[selector] = None

            ha.index.min            
            
            emptylist.append(ha)
            print '---------------------'
            print 'Read file sucessfully!'
            print '---------------------'
            break
        except AttributeError:
            skip = skip+1
            if skip > 30:
                print 'something wrong with ', eachStatNr
                # erroneous_files.append(eachStatNr)
                break
            else:
                print 'AttributeError detected, skip ',skip, 'lines in header'

        except ValueError:
            skip = skip+1
            if skip > 30:
                print 'something wrong with ', eachStatNr
                # erroneous_files.append(eachStatNr)
                break
            else:
                print 'ValueError detected, skip ',skip, 'lines in header'
    del skip

df_ahyd_all = pd.concat(emptylist, axis=1)
# 17 stations are missing here that gave an error in reading
# next step identifies the erroneous stations


# compare the columns of df_ahyd_all (=successfully read) with statlist, this
# also give erroneous files
fail_stations = []
success_stations = df_ahyd_all.columns.values
statlist_AHYD

# identify the fail stations not yet successfully read
for eachElement in statlist_AHYD:
    print 'test station ', eachElement
    if eachElement not in success_stations:
        fail_stations.append(eachElement)

df_ahyd_all.to_pickle(src + '\AHYD_dailysums_raw.npy')


# -----------------------------------
# ----------------- Repair dataframe (edited 2015-07-10)
# -----------------------------------

df_ahyd_all_raw = pd.read_pickle(src + '\AHYD_dailysums_raw.npy')

'''
there are some erroneous data points, where one day has more than one 
observation'''

# first and last day of observations in file
start = df_ahyd_all_raw.index[0]
end = df_ahyd_all_raw.index[-1]

# span daily range between first and last day
correct_daily_range = pd.date_range(start, end, freq='1D')

# find number of errors (=additional days)
errors = len(df_ahyd_all_raw.index) - len(correct_daily_range)

# find strange datetime indices (should be 07:00:00 for all)
possible_errors_sec = np.where(df_ahyd_all_raw.index.second!=0)[0]
possible_errors_min = np.where(df_ahyd_all_raw.index.minute!=0)[0]
possible_errors_hour = np.where(df_ahyd_all_raw.index.hour!=7)[0]

# indices of strange dates
ind_err = np.unique(np.concatenate((possible_errors_hour,
                                       possible_errors_min,
                                       possible_errors_sec), axis=0))                               
strange_dates = df_ahyd_all_raw.index[ind_err] 

# Dataframe with all weird times in it:
dates_list = []
for ID in range(len(strange_dates)):
    entry = df_ahyd_all_raw[str(strange_dates[ID])]
    dates_list.append(entry)    
all_dates_errors = pd.concat(dates_list, axis=0, join='outer') 

# drop rows where all values are NAN                                  
all_dates_errors_not_NAN = all_dates_errors.dropna(how='all')

# gives the station that had the highest value for the day for each date 
all_dates_errors_not_NAN.idxmax(axis=1).dropna(how='all')

# for each station the date where the station had its max
all_dates_errors_not_NAN.idxmax(axis=0).dropna(how='all')

''' 
* 34 observations are shifted by max 30 min (07:30 to 07:00)
* 8 observations are deleted, i.e. set to missing value (2 of them were 0 at
00:00 and 17:26:45 and 6 were missing values at strange times)
* for Station 112730 May 1998'''

for day in range(1,31):
    df_ahyd_all_raw.ix['1998-05-'+ str(day) + ' 07:00:00', '112730'
                   ] = np.float(df_ahyd_all_raw['112730']['1998-05-'+ str(day)+
                                                      ' 07:30:00'])
# rewrite values to 7:000:00 when time is close to 7am                                                       
df_ahyd_all_raw.ix['1998-03-01 07:00:00', '111310'
               ] = np.float(df_ahyd_all_raw['111310']['1998-03-01 07:30:00'])
df_ahyd_all_raw.ix['1998-03-02 07:00:00', '114868'
               ] = np.float(df_ahyd_all_raw['114868']['1998-03-02 06:59:55'])
df_ahyd_all_raw.ix['2008-07-17 07:00:00', '111476'
               ] = np.float(df_ahyd_all_raw['111476']['2008-07-17 07:00:05'])
df_ahyd_all_raw.ix['2009-09-25 07:00:00', '113803'
               ] = np.float(df_ahyd_all_raw['113803']['2009-12-25 07:00:05'])

# delete the rows where the time is not 07:00:00
df_ahyd_all_raw = df_ahyd_all_raw[df_ahyd_all_raw.index.hour == 7]
df_ahyd_all_raw = df_ahyd_all_raw[df_ahyd_all_raw.index.minute == 0]
df_ahyd_all_raw = df_ahyd_all_raw[df_ahyd_all_raw.index.second == 0]

# test
errors_test = len(df_ahyd_all_raw.index) - len(correct_daily_range)

if errors_test==0:
    df_ahyd_all_raw.index = correct_daily_range
    df_ahyd_all_raw.to_pickle(src + '\AHYD_dailysums.npy')
else:
    print 'Error! Check for inconsistencies'
    
''' ---------------------------------------------------
EDIT 23.7.2015:
-------------------------------------------------------
---------------------------------------------------
- found out that one stationnumber in List was duplicated (114801)
- Values of statnr 114793 were missing instead
- following snipped changed that series in place of the npy
'''

eachStatNr = '114793'

emptylist = []
skip=20
while True:
    try:
        print 'skipping ', skip, 'lines in header'
        ha = pd.read_csv(str(pth) + '\N-Tagessummen-' + eachStatNr + '.csv',
                         sep=';', skipinitialspace=True, header=None,
                         skiprows=skip, index_col=0, parse_dates=True,
                         dayfirst=True, names=['date',str(eachStatNr)],
                         skipfooter=1, engine='python')

        # ha[str(eachStatNr)] = ha[str(eachStatNr)].apply(lambda x: x.replace(",",".")).astype(float)
        ha[eachStatNr] = ha[eachStatNr].apply(lambda x: x.replace(",",".")).astype(float)
        # replace missing values with NaN
        selector = ha<0
        ha[selector] = None

        ha.index.min            
        
        emptylist.append(ha)
        print '---------------------'
        print 'Read file sucessfully!'
        print '---------------------'
        break
    except AttributeError:
        skip = skip+1
        if skip > 30:
            print 'something wrong with ', eachStatNr
            # erroneous_files.append(eachStatNr)
            break
        else:
            print 'AttributeError detected, skip ',skip, 'lines in header'

    except ValueError:
        skip = skip+1
        if skip > 30:
            print 'something wrong with ', eachStatNr
            # erroneous_files.append(eachStatNr)
            break
        else:
            print 'ValueError detected, skip ',skip, 'lines in header'
del skip

# drops the duplicate column of stations ['114801']
AHYD_all_stations_1 = AHYD_all_stations.T.groupby(level=0).first().T

AHYD_all_stations_2 = pd.concat((AHYD_all_stations_1, ha), axis=1)

AHYD_all_stations_2.to_pickle(src + '\AHYD_dailysums.npy')








