# -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 10:51:39 2015

@author: Kaddabadda
"""

''' ---------------------------------------------------------------------------
READ ZAMG DAILY DATA TO DATAFRAME
-------------------------------------------------------------------------------
'''
import numpy as np
import pandas as pd
import csv
import os

''' paths to raw input files and station list'''
pi = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\Daily_data_single_files'
tbl_p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\Station_Dataframes\ZAMG_stations_SW_Alps_150216.csv'   
station_id = pd.read_csv(tbl_p, index_col=1, usecols=['statnr', 'synnr'],
                         parse_dates=0,
                         dtype='str')

dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d')
emptylist = []
for nr in  station_id['statnr']:
    Daily_Tmax = pd.read_csv(pi+'\zamg_tag_station'+str(nr)+'.txt',
                          index_col=0,
                          usecols=[0, 2], #change for other variables
                          parse_dates=[0],
                          date_parser = dateparse, #YYYYMMDD, see above
                          skiprows=2,
                          sep=';',
                          header=None, 
                          # use synnr as station ID (as in 10min data)
                          names=['',str(station_id[station_id.statnr==
                                 str(nr)].index[0])],
                          skipfooter=1, 
                          na_values=['999.900000'])
    Daily_Tmax = Daily_Tmax[Daily_Tmax.index.year>1991]
    emptylist.append(Daily_Tmax)

ZAMG_daily_Tmax = pd.concat(emptylist, axis=1)
ZAMG_daily_Tmax.to_pickle(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\DAILY\ZAMG_daily_Tmax_1992-2004.npy')

           