# -*- coding: utf-8 -*-
"""
Created on Tue May 26 16:31:32 2015

@author: Kaddabadda

create a shapefile with AHYD stations within the study region
"""

import pandas as pd
import numpy as np
import csv as csv
pth = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'

ha = pd.read_csv(str(pth) + '\Stationen_AHYD_DailySumData.csv', skipinitialspace=True,
                 header = 0, usecols = ['HZBNR', 'Name', 'lat', 'lon', 'z', 'seit'])


l = len(np.array(ha['lat']))
lat = []
lon = []

for i in range(l):
    lat.append(str(np.array(ha['lat'][i]))[0:2] + '/' + str(np.array(ha['lat']\
               [i]))[3:5] + "/" + str(np.array(ha['lat'][i]))[6:8])
    lon.append(str(np.array(ha['lon'][i]))[0:2] + '/' + str(np.array(ha['lon']\
               [i]))[3:5] + "/" + str(np.array(ha['lon'][i]))[6:8])

years = 2014-ha.seit

ha_new = pd.DataFrame([np.array(ha.HZBNR), np.array(ha.Name), np.array(lat),
np.array(lon), np.array(ha.z), np.array(ha.seit), np.array(years)]).transpose()


ha_new.to_csv(str(pth) + '\AHYD_stations_DailySumData_shape.csv', header = ['HZBNR',
              'name', 'lat', 'lon', 'altitude', 'year1', 'rec_length'])