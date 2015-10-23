# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 10:30:59 2015

@author: Kaddabadda
convert lat and lon from DMS to Decimal Degrees
when saved as [other columns],DD MM SS,[other columns]
"""

import pandas as pd

f = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
f_in = '\AHYD_all_HighRes_Stations.csv'
f_out = '\AHYD_all_HighRes_Stations_DD.csv'

stations = pd.read_csv(f+f_in,
                       index_col=[0])

stations['DDLat'] =  [((float(i[6:8])/3600) +
                            (float(i[3:5])/60) +
                            (float(i[0:2]))) for i in stations['Lat']]
stations['DDLon'] =  [((float(i[6:8])/3600) +
                            (float(i[3:5])/60) +
                            (float(i[0:2]))) for i in stations['Lon']]          

stations.to_csv(f+f_out)   


''' print date of first valid precip measurement'''
pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'

for i in ZAMG_all_stations.columns:
    print 'Station', i, '\n'
    first = ZAMG_all_stations[i].dropna().index[0]
    print first, '\n', '\n'
    
'''delete Sonnblick and Kolm-Saigurn'''
''' DELETED 2015-10-16 KSC '''    
ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min_allyear.npy')

del ZAMG_all_stations['11344']
del ZAMG_all_stations['11343']

ZAMG_all_stations.to_pickle(pth2 + '\ZAMG_10min_allyear.npy')
