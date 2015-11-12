# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 08:21:18 2015

@author: Kaddabadda
*** read variable from ZAMG Station files to pandas dataframe and save as npy
"""

import Modules.ZAMG_tawes.stationfiles_v9 as zamg
import pandas as pd
import numpy as np

print zamg.var_key

p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG'
stationlist = pd.read_csv(p + '\SEA_stations_ZAMG_151015.csv', 
                          index_col=None,
                          usecols=[0, 1, 2, 3, 4, 5, 6])

''' ---------------------------------------------------------------------------
READ ZAMG 10MIN DATA TO DATAFRAME
-------------------------------------------------------------------------------
'''                          

def ZAMG_10min_to_npy(var):
    '''INPUT:
    *** var: variable to be read into dataframe, use chiffre from zamg.var_key
    (numbers 1-10)
    '''
    if var<0 or var>10:
        print ' !!! Variable number not valid (chose numbers 1-10) !!!'
        return
    else:
        variable = zamg.var_key.values()[var]
        print 'read ', variable    
    
    emptylist = []
    pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes' 
    
    for eachStation in stationlist['synnr']:
        print 'processing statnr: ', eachStation
    
        df = pd.read_csv(pth2 + '\DataFrame_' + str(eachStation) + '.csv', 
                         index_col=0,
                         usecols=[0,'precip'], 
                         parse_dates=True)
    
        # selector extended summer months AMJJASO
        month = df.index.month
        selector = ((1 <= month) & (month <= 12))
        data = df.iloc[:,[0]][selector] #precip[selector]
        data.columns = [eachStation]
        del df
        emptylist.append(data)
    
    ZAMG_all_stations = pd.concat(emptylist, axis=1)
    
    ZAMG_all_stations.to_pickle(pth2 + '\ZAMG_10min_allyear_' + variable +
                                '.npy')

''' ---------------------------------------------------------------------------
READ ZAMG DAILY DATA TO DATAFRAME
-------------------------------------------------------------------------------
'''

''' paths to raw input files and station list'''
pi = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\Downloaded_data_raw\Daily_data_single_files'
tbl_p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\Station_Dataframes\ZAMG_stations_SW_Alps_150216.csv'   


dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d')
emptylist = []
for eachStation in stationlist['statnr']:
    print 'processing statnr: ', eachStation
    Daily_Tmax = pd.read_csv(pi+'\zamg_tag_station'+str(eachStation)+'.txt',
                          index_col=0,
                          usecols=[0, 2], #change for other variables
                          parse_dates=[0],
                          date_parser = dateparse, #YYYYMMDD, see above
                          skiprows=2,
                          sep=';',
                          header=None, 
                          # use synnr as station ID (as in 10min data)
                          names=[stationlist['synnr']],
                          skipfooter=1, 
                          na_values=['999.900000'])
    Daily_Tmax = Daily_Tmax[Daily_Tmax.index.year>1991]
    emptylist.append(Daily_Tmax)

ZAMG_daily_Tmax = pd.concat(emptylist, axis=1)
ZAMG_daily_Tmax.to_pickle(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\DAILY\ZAMG_daily_Tmax_1992-2004.npy')

''' ---------------------------------------------------------------------------
WRITE ZAMG 10min to single station files (09.11.2015)
-------------------------------------------------------------------------------
'''          
p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\Station_Dataframes'
f = r'\ZAMG_10min_allyear.npy'

ZAMG_all = pd.read_pickle(p+f)

for column in ZAMG_all.columns:
    print column
    stationseries = ZAMG_all[column]
    stationseries.to_pickle(p+'\ZAMGStationSeries\ZAMG_HR_' + column + '.npy')
   

