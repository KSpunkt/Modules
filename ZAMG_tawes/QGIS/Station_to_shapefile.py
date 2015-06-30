# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 20:06:49 2015

@author: Kaddabadda
rewrite Stationlist of ZAMG stations to create QGIS layer
"""
import pandas as pd
import numpy as np
import csv as csv
pth = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG'

ha = pd.read_csv(str(pth) + '\ZAMG_stations_SW_Alps_150216.csv', skipinitialspace=True,
                 header = 0, usecols = ['statnr', 'synnr', 'name', 'lon', 'lat', 'altitude', 'begindate'])

l = len(np.array(ha['lat']))
lat = []
lon = []
year1 = []
for i in range(l):
    lat.append(str(np.array(ha['lat'][i]))[0:2] + '°' + str(np.array(ha['lat']\
               [i]))[2:4] + "'" + str(np.array(ha['lat'][i]))[4:6] + "''")
    lon.append(str(np.array(ha['lon'][i]))[0:2] + '°' + str(np.array(ha['lon']\
               [i]))[2:4] + "'" + str(np.array(ha['lon'][i]))[4:6] + "''")
    year1.append(str(np.array(ha['begindate'][i]))[0:4])

ha_new = pd.DataFrame([np.array(ha.statnr), np.array(ha.synnr), np.array(ha.name), np.array(lat),
          np.array(lon), np.array(ha.altitude), np.array(ha.begindate), np.array(year1)]).transpose()


ha_new.to_csv(str(pth) + '\ZAMG_stations_SW_Alps_shape.csv', header = ['statnr',
              'synnr', 'name', 'lat', 'lon', 'altitude', 'begindate', 'year1'])