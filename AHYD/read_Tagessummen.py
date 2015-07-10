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

df_ahyd_all.to_pickle(src + '\AHYD_dailysums.npy')
# -----------------------------------
# ----------------- Repair dataframe (edited 2015-07-10)
# -----------------------------------
df_ahyd_all = pd.read_pickle(src + '\AHYD_dailysums.npy')

# there are some erroneous data points, where one day has more than one 
# observation

# first and last day of observations in file
start = df_ahyd_all.index[0]
end = df_ahyd_all.index[-1]

# span daily range between first and last day
correct_daily_range = pd.date_range(start, end, freq='1D')

# find number of errors (=additional days)
errors = len(df_ahyd_all.index) - len(correct_daily_range)

# find strange datetime indices (should be 07:00:00 for all)
possible_errors_sec = np.where(df_ahyd_all.index.second!=0)[0]
possible_errors_min = np.where(df_ahyd_all.index.minute!=0)[0]
possible_errors_hour = np.where(df_ahyd_all.index.hour!=7)[0]

# indices of strange dates
ind_err = np.unique(np.concatenate((possible_errors_hour,
                                       possible_errors_min,
                                       possible_errors_sec), axis=0))                               
strange_dates = df_ahyd_all.index[ind_err]   

dates_list = []
for ID in range(len(strange_dates)):
    entry = df_ahyd_all[str(strange_dates[ID])[0:10]]
    dates_list.append(entry)
        
all_dates_errors = pd.concat(dates_list, axis=0, join='outer')   


dates_list = []
for ID in range(len(strange_dates)):
    entry = df_ahyd_all[str(strange_dates[ID])]
    dates_list.append(entry)
        
all_dates_errors = pd.concat(dates_list, axis=0, join='outer') 

                                  
greater100 = all_dates_errors[all_dates_errors>0]
all_dates_errors = all_dates_errors.dropna(how='all')

# gives for each date the station that had the highest value for the day
all_dates_errors.idxmax(axis=1).dropna(how='all')

# for each station the date where the station had its max
all_dates_errors.idxmax(axis=0).dropna(how='all')














