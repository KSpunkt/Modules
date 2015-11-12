# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:16:37 2015

@author: Kaddabadda
-------------------------------------------------------------------------------
AHYD HIGH RESOLUTION PRECIPITATION OBSERVATIONS
-------------------------------------------------------------------------------
* read, process and quality control the high resolution station data as
  provided by the provincial AHYD authorities:
  - Salzburg
  - Burgenland
  - Tirol
  - Niederoesterreich
  - Kaernten
  - Steiermark
* each are provided in slightly different formats, which requires case-by-case
  processing
* a quality controlled (in terms of date, time and NaN consistency)
  [HZBNR].npy is stored for each station individually
* additionally, all stations are combined in one dataframe, which is, however,
  too large to be easily processed further.
"""
import pandas as pd
import numpy as np

pout = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution\edited_for_processing'
p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution'

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
for each file:
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

filename, header lines'''

nrs = [
       ['\N110239', 26],
       ['\N111278', 26],
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
for each file:
filename, header lines'''
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
nrs = [
       ['\NNL1028', 28], 
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


'''----------------------------------------------------------------------------
ALL STATIONS DATAFRAME
-------------------------------------------------------------------------------
* combines all highres AHYD 5min files in one DataFrame (8GB)
* 
* one set is HDNR
* five sets are HZBNR
'''

'''external hard drive paths'''
#pout = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution\edited_for_processing'
#p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\High_resolution'
'''local kaddabadda lenovo paths'''
pout = r'D:\Documents\AHYD\edited_for_processing'
p = r'D:\Documents\AHYD\edited_for_processing'
'''WEGC Linux ksc paths'''
#pout = r'\data\arsclisys\acu\ksc\WEGC\02_PhD_research\03_Data\AHYD\High_resolution\edited_for_processing'
#p = r'\data\arsclisys\acu\ksc\WEGC\02_PhD_research\03_Data\AHYD\High_resolution'

'''load list od stations within SEA'''
stationlist_AHYD = pd.read_excel(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\AHYD_hires_SEA.xlsx',
                               parse_cols = [0,3,4,5], 
                               index_col = [0])
AHYD_dict = {}

for HZBNR in stationlist_AHYD['HZBNR']:
        try: 
            frame = pd.read_pickle(pout+ '\AHYD_'+ str(HZBNR) +'.npy')
            frame.columns = [str(HZBNR)]
            
            '''uncomment for Mar-Nov 1992-2015'''
#            frame = frame[frame.index.year>1991]
#            month = frame.index.month
#            selector = ((3 <= month) & (month <= 11))
#            frame = frame[selector]
            
            print 'process HZBNR:', HZBNR
            AHYD_dict.update({str(HZBNR): frame})
        except IOError:
            HDNR = str(int(stationlist_AHYD['HDNR'].where(stationlist_AHYD['HZBNR']==HZBNR).dropna().values[0]))
            print 'no HZBNR for', HZBNR, ', use HDNR:', HDNR 
            frame = pd.read_pickle(pout+ '\AHYD_'+ HDNR +'.npy')
            frame.columns = [str(HZBNR)]
            
            '''uncomment for Mar-Nov 1992-2015'''
#            frame = frame[frame.index.year>1991]
#            month = frame.index.month
#            selector = ((3 <= month) & (month <= 11))
#            frame = frame[selector]            
            
            AHYD_dict.update({str(HZBNR): frame})
            del frame

'''---'''            
AHYD_hires_SEA = pd.concat(AHYD_dict, axis=1)

#AHYD_hires_SEA.to_pickle(pout+ '\AHYD_hires_SEA_MarNov_92.npy')
AHYD_hires_SEA.to_pickle(pout+ '\AHYD_hires_SEA_all.npy')


'''----------------------------------------------------------------------------
PROCESS ALL STATION FILES individually, as all together in a dataframe result 
in a too large file (8GB), with the longest record starting in 1956, and all
other stations being fillep up to that with NaNs
-------------------------------------------------------------------------------
* Process each station series and identify events
* extract highest events (p95) and continue working with that
'''
import pandas as pd
pout =u'/data/arsclisys/acu/ksc/'

decades = [['61-69', [1961, 1969]],
           ['70-79', [1970, 1979]],
           ['80-89', [1980, 1989]],
           ['90-99', [1990, 1999]],
           ['00-11', [2000, 2011]],
           ['12-14', [2012, 2014]]]

decades = [['00-11', [2000, 2011]],
           ['12-14', [2012, 2014]]]


AHYD_hires_SEA = pd.read_pickle(pout+ '/AHYD_hires_SEA_all.npy')

for i, decade in enumerate(decades):
    print 'process decade', decade[0]
    selector = np.logical_and(AHYD_hires_SEA.index.year >= decade[1][0], AHYD_hires_SEA.index.year <= decade[1][1])
    AHYD_hires_SEA[selector].to_pickle(pout + '\AHYD_highres_' + decade[0] + '.npy')

selector = np.logical_and(AHYD_hires_SEA.index.year >= 2012, AHYD_hires_SEA.index.year <= 2014)
AHYD_hires_SEA[selector].to_pickle(pout + '\AHYD_highres_12-14.npy')    

selector = np.logical_and(AHYD_hires_SEA.index.year >= 2000, AHYD_hires_SEA.index.year <= 2005)
AHYD_hires_SEA[selector].to_pickle(pout + '\AHYD_highres_00-05.npy')    

selector = np.logical_and(AHYD_hires_SEA.index.year >= 2006, AHYD_hires_SEA.index.year <= 2011)
AHYD_hires_SEA[selector].to_pickle(pout + '\AHYD_highres_06-11.npy')    

''' save station time series'''
pout =u'/data/arsclisys/acu/ksc/AHYDStationSeries'
AHYD_hires_SEA.columns =  AHYD_hires_SEA.columns.get_level_values(0)
for column in AHYD_hires_SEA:
    print 'processing station', column
    stationseries = AHYD_hires_SEA[column]
    stationseries.to_pickle(pout + '/AHYD_HR_station_' + column + '.npy')



