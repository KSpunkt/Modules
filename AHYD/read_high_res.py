# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:16:37 2015

@author: Kaddabadda
Reads daily precipitation sums from N-Tagessummenfiles from AHYD into one dataframe
"""
import pandas as pd
import numpy as np
import csv as csv

pout = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution\edited_for_processing'
p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution'

#stationlist_AHYD = pd.read_csv(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\SEA_stations_AHYD_151015.csv',
#                               usecols = [1,2], 
#                               index_col = [1])

'''----------------------------------------------------------------------------
SALZBURG
-------------------------------------------------------------------------------
issues with this file:
*HZBNR
* minute intervals are at minutes 9 and 5 instead of 5 and 0
procedures:
* reindex to 5 and 0
'''
f = r'\AHYD_Salzburg\N115055\N115055.csv'

'''  for each file:
filename, header lines, first observation, last observation'''
#nrs = [['\N115055', 28, '25.02.2007 22:19:00', '30.06.2015 08:44:00']]
nrs = [['\N115055', 28, '25.02.2007 22:20:00', '30.06.2015 08:45:00']]

for i in nrs:    
    nr = i[0]
    skip = i[1]
    first = i[2]
    last = i[3]
    idx = pd.date_range(first, last, freq='5min')
    print nr, skip
    f = '\AHYD_Salzburg' + nr + '.csv'

    ha = pd.read_csv(p+f,
                     sep=';', 
                     decimal=',',
#                     delim_whitespace=True,
                     skipinitialspace=True, 
                     header=None,
                     skiprows=skip, 
                     index_col=0, 
                     parse_dates=True,
                     names=['date', 'precip'],
#                     parse_dates={"datetime": [0,1]},
#                     names=['date', 'time', 'precip'],
                     dayfirst=True, 
                     na_values=['Luecke'],
#                     nrows=100000 # for testing
                     )
    ha.precip.astype(float) # convert to float
    # sort by index to guarantuee correct time series
    ha.sort_index(kind='mergesort',
                  inplace=1)
    '''fill missing dates with the last valid or NaN value (Intervallwerte!)
    idx for reindexing has been shifted by 1 minute and minute 9 to 10 and
    minute 4 to 5, so 00:19 -> 00:20 and 00:24 -> 00:25'''
                  
    ha_rix = ha.reindex(index=idx,
                        method='ffill')
    ha_rix.to_pickle(pout+ '\AHYD_'+ nr[2:]+'.npy')



'''----------------------------------------------------------------------------
TIROL
-------------------------------------------------------------------------------
*HZBNR
'''

'''  for each file:
filename, header lines'''
nrs = [['\N113001', 28], 
       ['\N113019', 26], 
       ['\N113043', 24], 
       ['\N113050', 28],
       ['\N113589', 26], 
       ['\N114926', 26], 
       ['\N114934', 26]]
for i in nrs:    
    nr = i[0]
    skip = i[1]
    print nr, skip
    f = '\AHYD_Tirol' + nr + '.csv'

    ha = pd.read_csv(p+f,
                     sep=';', 
                     decimal=',',
#                     delim_whitespace=True,
                     skipinitialspace=True, 
                     header=None,
                     skiprows=skip, 
                     index_col=0, 
                     parse_dates=True,
                     names=['date', 'precip'],
#                     parse_dates={"datetime": [0,1]},
#                     names=['date', 'time', 'precip'],
                     dayfirst=True, 
                     na_values=['Luecke'],
#                     nrows=100000 # for testing
                     )
    ha.precip.astype(float) # convert to float
    # sort by index to guarantuee correct time series
    ha.sort_index(kind='mergesort',
                  inplace=1)
    '''fill missing dates with the last valid or NaN value (Intervallwerte!)
    idx for reindexing has been shifted by 1 minute and minute 9 to 10 and
    minute 4 to 5, so 00:19 -> 00:20 and 00:24 -> 00:25'''
    first = ha.index[0]
    last = ha.index[-1]
    idx = pd.date_range(first, last, freq='5min')              
    ha_rix = ha.reindex(index=idx,
                        method='ffill')
    ha_rix.to_pickle(pout+ '\AHYD_'+ nr[2:]+'.npy')

'''----------------------------------------------------------------------------
NIEDEROESTERREICH
-------------------------------------------------------------------------------
issues with the files:
*HZBNR
* files are huge
* values are valid until next interval:
* delimiter = tab
* delimiter = tab also implied that date and time are read as two separate cols
* decimal = '.'
* headers are all 26 lines
* missing values = Lücke with Umlaut ü, problem with encoding
* times are not consistent (i.e., april might follow after september)
* sometimes errors in the line break, or date is cut at some point in the str,
  i.e., 14.05.2014 17:cke

procedure:
* use emacs to replace all ü with ue
* sort dataframe by date to clean wrong consecutive months
* create complete index and reindex dataframe with that one, fill in missing
  values using the last valid observation ()

'''

''' filename, header lines'''
nrs = [
#       ['\N110239', 26],
#       ['\N111278', 26],
       ['\N110254', 27]]

for i in nrs:    
    nr = i[0]
    skip = i[1]
    print nr, skip
    f = '\AHYD_Niederoesterreich' + nr + '.dat'

    ha = pd.read_csv(p+f,
#                     sep=';', 
#                     decimal=',',
                     delim_whitespace=True,
                     skipinitialspace=True, 
                     header=None,
                     skiprows=skip, 
                     index_col=0, 
                     parse_dates={"datetime": [0,1]},
                     dayfirst=True, 
                     na_values=['Luecke'],
                     names=['date', 'time', 'precip'],
#                     nrows=100000
                     )
    ha.precip.astype(float) # convert to float (not recognized because of 'Lücke')
    # sort by index, as months and dates seem to get mixed up sometimes
    ha.sort_index(kind='mergesort',
                  inplace=1)
    first = ha.index[0]
    last = ha.index[-1]
    idx = pd.date_range(first, last, freq='5min')  
    # fill missing dates with the last value (Intervallwerte!)              
    ha_rix = ha.reindex(index=idx,
               method='ffill')
    ha_rix.to_pickle(pout+ '\AHYD_'+ nr[2:]+'.npy')


'''----------------------------------------------------------------------------
KÄRNTEN
-------------------------------------------------------------------------------
issues with these files:
*HDNR
'''
'''  for each file:
filename, header lines, first observation, last observation'''
nrs = [['\N2000004', 24], 
       ['\N2000005', 26], 
       ['\N2000009', 24], 
       ['\N2000014', 24], 
       ['\N2000025', 24], 
       ['\N2000031', 24], 
       ['\N2000034', 24], 
       ['\N2000038', 24], 
       ['\N2000040', 24], 
       ['\N2000046', 24], 
       ['\N2000047', 24], 
       ['\N2000050', 24], 
       ['\N2000058', 24], 
       ['\N2000061', 24], 
       ['\N2000065', 26], 
       ['\N2000068', 24], 
       ['\N2000069', 24], 
       ['\N2000074', 24], 
       ['\N2000076', 24], 
       ['\N2000079', 24], 
       ['\N2000080', 24], 
       ['\N2000086', 24], 
       ['\N2000091', 24], 
       ['\N2000098', 24], 
       ['\N2000100', 24], 
       ['\N2000109', 24], 
       ['\N2000112', 26], 
       ['\N2000113', 24], 
       ['\N2000115', 24], 
       ['\N2000116', 26], 
       ['\N2000117', 24], 
       ['\N2000124', 24], 
       ['\N2000132', 24], 
       ['\N2000133', 24], 
       ['\N2000134', 24],
       ['\N2000139', 24], 
       ['\N2000140', 24], 
       ['\N2000141', 24], 
       ['\N2000144', 26], 
       ['\N2000145', 24], 
       ['\N2000146', 24], 
       ['\N2000148', 24], 
       ['\N2000151', 24], 
       ['\N2000153', 24], 
       ['\N2000156', 24], 
       ['\N2000157', 24], 
       ['\N2000158', 26], 
       ['\N2000161', 24], 
       ['\N2002171', 24], 
       ['\N2002175', 26], 
       ['\N2002176', 25],
       ['\N2002178', 24], 
       ['\N2002358', 24], 
       ['\N2002468', 24], 
       ['\N2002469', 24],
       ['\N2002476', 24], 
       ['\N2002478', 24], 
       ['\N2002587', 24], 
       ['\N2002588', 24],
        ]

for i in nrs:    
    nr = i[0]
    skip = i[1]
    print nr, skip
    f = '\AHYD_Kaernten\kaer_in' + nr + '.dat'

    ha = pd.read_csv(p+f,
#                     sep=';', 
#                     decimal=',',
                     delim_whitespace=True,
                     skipinitialspace=True, 
                     header=None,
                     skiprows=skip, 
                     index_col=0, 
#                     parse_dates=True,
##                     names=['date', 'precip'],
                     parse_dates={"datetime": [0,1]},
                     names=['date', 'time', 'precip'],
                     dayfirst=True, 
                     na_values=['Luecke'],
#                     nrows=100000 # for testing
                     )
    ha.precip.astype(float) # convert to float
       
    # sort by index to guarantuee correct time series
    ha.sort_index(kind='mergesort',
                  inplace=1)
    '''fill missing dates with the last valid or NaN value (Intervallwerte!)
    idx for reindexing has been shifted by 1 minute and minute 9 to 10 and
    minute 4 to 5, so 00:19 -> 00:20 and 00:24 -> 00:25'''
    first = ha.index[0]
    last = ha.index[-1]
    idx = pd.date_range(first, last, freq='5min')              
    ha_rix = ha.reindex(index=idx,
                        method='ffill')
    int(nr[2:])                    
    ha_rix.to_pickle(pout+ '\AHYD_'+ nr[2:]+'.npy')

'''----------------------------------------------------------------------------
BURGENLAND
-------------------------------------------------------------------------------
issues with these files:
* HZBNR
'''
'''  for each file:
filename, header lines, first observation, last observation'''
nrs = [
       ['\N105080', 24], 
       ['\N106724', 24], 
       ['\N110064', 28], 
       ['\N110080', 26],
       ['\N110312', 26], 
       ['\N110346', 26], 
       ['\N110379', 26],
       ['\N110395', 26], 
       ['\N110544', 26], 
       ['\N110627', 28],
       ['\N110668', 26], 
       ['\N110692', 26], 
       ['\N110726', 24],
       ['\N110734', 28], 
       ['\N110742', 26], 
       ['\N110775', 24],
       ['\N111112', 26], 
       ['\N111146', 26], 
       ['\N111443', 26],
       ['\N111450', 28], 
       ['\N111468', 26], 
       ['\N122010', 24],
       ['\N122804', 24], 
       ]
for i in nrs:    
    nr = i[0]
    skip = i[1]
    print nr, skip
    f = '\AHYD_Burgenland\WegenerCenterN' + nr + '.csv'

    ha = pd.read_csv(p+f,
                     sep=';', 
                     decimal=',',
#                     delim_whitespace=True,
                     skipinitialspace=True, 
                     header=None,
                     skiprows=skip, 
                     index_col=0, 
                     parse_dates=True,
                     names=['date', 'precip'],
#                     parse_dates={"datetime": [0,1]},
#                     names=['date', 'time', 'precip'],
                     dayfirst=True, 
                     na_values=['Luecke'],
#                     nrows=100000 # for testing
                     )
    ha.precip.astype(float) # convert to float
    # sort by index to guarantuee correct time series
    ha.sort_index(kind='mergesort',
                  inplace=1)
    '''fill missing dates with the last valid or NaN value (Intervallwerte!)
    idx for reindexing has been shifted by 1 minute and minute 9 to 10 and
    minute 4 to 5, so 00:19 -> 00:20 and 00:24 -> 00:25'''
    first = ha.index[0]
    last = ha.index[-1]
    idx = pd.date_range(first, last, freq='5min')               
    ha_rix = ha.reindex(index=idx,
                        method='ffill')
    ha_rix.to_pickle(pout+ '\AHYD_'+ nr[2:]+'.npy')


'''----------------------------------------------------------------------------
STEIERMARK
-------------------------------------------------------------------------------
issues with these files:
* HZBNR
'''
nrs = [['\NNL1028', 28], 
       ['\NNL1030', 26], 
       ['\NNL1060', 24], 
       ['\NNL1141', 26],
       ['\NNL1210', 22], 
       ['\NNL1510', 24], 
       ['\NNL1538', 24],
       ['\NNL1590', 24], 
       ['\NNL1605', 24], 
       ['\NNL1620', 24],
       ['\NNL1740', 24], 
       ['\NNL2010', 24], 
       ['\NNL2141', 26],
       ['\NNL2310', 24], 
       ['\NNL2320', 24], 
       ['\NNL2610', 26],
       ['\NNL2637', 24], 
       ['\NNL2915', 24], 
       ['\NNL3008', 28],
       ['\NNL3100', 24], 
       ['\NNL3341', 26], 
       ['\NNL3385', 24],
       ['\NNL3390', 26], 
       ['\NNL3510', 24], 
       ['\NNL3642', 24],
       ['\NNL3665', 24], 
       ['\NNL3778', 24], 
       ['\NNL3790', 24],
       ['\NNL3828', 24], 
       ['\NNL3830', 24], 
       ['\NNL3870', 26], 
       ['\NNL3890', 24],
       ['\NNL3915', 24], 
       ['\NNL4033', 24], 
       ['\NNL4525', 24],
       ['\NNL4540', 24], 
       ['\NNL4571', 24], 
       ['\NNL4576', 23],
       ['\NNL4580', 24], 
       ['\NNL4595', 24], 
       ['\NNL4610', 24],
       ['\NNL4641', 24], 
       ['\NNL4648', 24], 
       ['\NNL4667', 24], 
       ['\NNL5040', 24],
       ]
for i in nrs:    
    nr = i[0]
    skip = i[1]
    print nr, skip
    f = '\AHYD_Steiermark' + nr + '.csv'

    ha = pd.read_csv(p+f,
                     sep=';', 
                     decimal=',',
#                     delim_whitespace=True,
                     skipinitialspace=True, 
                     header=None,
                     skiprows=skip, 
                     index_col=0, 
                     parse_dates=True,
                     names=['date', 'precip'],
#                     parse_dates={"datetime": [0,1]},
#                     names=['date', 'time', 'precip'],
                     dayfirst=True, 
                     na_values=['Luecke'],
#                     nrows=100000 # for testing
                     )
    ha.precip.astype(float) # convert to float
    # sort by index to guarantuee correct time series
    ha.sort_index(kind='mergesort',
                  inplace=1)
    '''fill missing dates with the last valid or NaN value (Intervallwerte!)
    idx for reindexing has been shifted by 1 minute and minute 9 to 10 and
    minute 4 to 5, so 00:19 -> 00:20 and 00:24 -> 00:25'''
    first = ha.index[0]
    last = ha.index[-1]
    idx = pd.date_range(first, last, freq='5min')              
    ha_rix = ha.reindex(index=idx,
                        method='ffill')
    ha_rix.to_pickle(pout+ '\AHYD_'+ nr[4:]+'.npy')

'''
pd.reindex()
reindex is an amazing function. It can (1) reorder existing data to match
a new set of labels, (2) insert new rows where no label previously existed,
(3) fill data for missing labels, (including by forward/backward filling)
(4) select rows by label!'''


'''each station csv has diffent number of header lines, thus try
different numbers  until no Error Message is raised
'''
#skip=24
#while True:
#    try:
#        print 'skipping ', skip, 'lines in header'
#        ha = pd.read_csv(p+f,
#                         sep=';', 
#                         decimal=',',
#                         skipinitialspace=True, 
#                         header=None,
#                         skiprows=skip, 
#                         index_col=0, 
#                         parse_dates=True,
#                         dayfirst=True, 
#                         names=['date', 'precip'],
##                         skipfooter=1, 
##                         engine='python', 
##                         na_values=[-999]
#                         )
#        ha.precip.astype(float)
#        selector = ha<0
#        ha[selector] = None
#        ha.resample('5min', how='sum', base=0)
#        
#      # ha[str(eachStatNr)] = ha[str(eachStatNr)].apply(lambda x: x.replace(",",".")).astype(float)
#        ha['precip'] = ha['precip'].apply(lambda x: x.replace(",",".")).astype(float)
#        # replace missing values with NaN
#        selector = ha<0
#        ha[selector] = None
#
#        ha.index.min            
#        
#        print '---------------------'
#        print 'Read file sucessfully!'
#        print '---------------------'
#        break
#    except AttributeError:
#        skip = skip+1
#        if skip > 30:
#            print 'something wrong with ', f
#            # erroneous_files.append(eachStatNr)
#            break
#        else:
#            print 'AttributeError detected, skip ',skip, 'lines in header'
#
#    except ValueError:
#        skip = skip+1
#        if skip > 30:
#            print 'something wrong with ', f
#            # erroneous_files.append(eachStatNr)
#            break
#        else:
#            print 'ValueError detected, skip ',skip, 'lines in header'
#del skip
#
#'''
#df_ahyd_all = pd.concat(emptylist, axis=1)
## 17 stations are missing here that gave an error in reading
## next step identifies the erroneous stations
#
#
## compare the columns of df_ahyd_all (=successfully read) with statlist, this
## also give erroneous files
#fail_stations = []
#success_stations = df_ahyd_all.columns.values
#statlist_AHYD
#
## identify the fail stations not yet successfully read
#for eachElement in statlist_AHYD:
#    print 'test station ', eachElement
#    if eachElement not in success_stations:
#        fail_stations.append(eachElement)
#
#df_ahyd_all.to_pickle(src + '\AHYD_dailysums_raw.npy')
#
#
## -----------------------------------
## ----------------- Repair dataframe (edited 2015-07-10)
## -----------------------------------
#
#df_ahyd_all_raw = pd.read_pickle(src + '\AHYD_dailysums_raw.npy')
#
#
#there are some erroneous data points, where one day has more than one 
#observation
#
## first and last day of observations in file
#start = df_ahyd_all_raw.index[0]
#end = df_ahyd_all_raw.index[-1]
#
## span daily range between first and last day
#correct_daily_range = pd.date_range(start, end, freq='1D')
#
## find number of errors (=additional days)
#errors = len(df_ahyd_all_raw.index) - len(correct_daily_range)
#
## find strange datetime indices (should be 07:00:00 for all)
#possible_errors_sec = np.where(df_ahyd_all_raw.index.second!=0)[0]
#possible_errors_min = np.where(df_ahyd_all_raw.index.minute!=0)[0]
#possible_errors_hour = np.where(df_ahyd_all_raw.index.hour!=7)[0]
#
## indices of strange dates
#ind_err = np.unique(np.concatenate((possible_errors_hour,
#                                       possible_errors_min,
#                                       possible_errors_sec), axis=0))                               
#strange_dates = df_ahyd_all_raw.index[ind_err] 
#
## Dataframe with all weird times in it:
#dates_list = []
#for ID in range(len(strange_dates)):
#    entry = df_ahyd_all_raw[str(strange_dates[ID])]
#    dates_list.append(entry)    
#all_dates_errors = pd.concat(dates_list, axis=0, join='outer') 
#
## drop rows where all values are NAN                                  
#all_dates_errors_not_NAN = all_dates_errors.dropna(how='all')
#
## gives the station that had the highest value for the day for each date 
#all_dates_errors_not_NAN.idxmax(axis=1).dropna(how='all')
#
## for each station the date where the station had its max
#all_dates_errors_not_NAN.idxmax(axis=0).dropna(how='all')
#
#
#* 34 observations are shifted by max 30 min (07:30 to 07:00)
#* 8 observations are deleted, i.e. set to missing value (2 of them were 0 at
#00:00 and 17:26:45 and 6 were missing values at strange times)
#* for Station 112730 May 1998
#
#for day in range(1,31):
#    df_ahyd_all_raw.ix['1998-05-'+ str(day) + ' 07:00:00', '112730'
#                   ] = np.float(df_ahyd_all_raw['112730']['1998-05-'+ str(day)+
#                                                      ' 07:30:00'])
## rewrite values to 7:000:00 when time is close to 7am                                                       
#df_ahyd_all_raw.ix['1998-03-01 07:00:00', '111310'
#               ] = np.float(df_ahyd_all_raw['111310']['1998-03-01 07:30:00'])
#df_ahyd_all_raw.ix['1998-03-02 07:00:00', '114868'
#               ] = np.float(df_ahyd_all_raw['114868']['1998-03-02 06:59:55'])
#df_ahyd_all_raw.ix['2008-07-17 07:00:00', '111476'
#               ] = np.float(df_ahyd_all_raw['111476']['2008-07-17 07:00:05'])
#df_ahyd_all_raw.ix['2009-09-25 07:00:00', '113803'
#               ] = np.float(df_ahyd_all_raw['113803']['2009-12-25 07:00:05'])
#
## delete the rows where the time is not 07:00:00
#df_ahyd_all_raw = df_ahyd_all_raw[df_ahyd_all_raw.index.hour == 7]
#df_ahyd_all_raw = df_ahyd_all_raw[df_ahyd_all_raw.index.minute == 0]
#df_ahyd_all_raw = df_ahyd_all_raw[df_ahyd_all_raw.index.second == 0]
#
## test
#errors_test = len(df_ahyd_all_raw.index) - len(correct_daily_range)
#
#if errors_test==0:
#    df_ahyd_all_raw.index = correct_daily_range
#    df_ahyd_all_raw.to_pickle(src + '\AHYD_dailysums.npy')
#else:
#    print 'Error! Check for inconsistencies'
#    
#'''








