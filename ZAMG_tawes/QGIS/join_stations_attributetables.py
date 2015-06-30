# -*- coding: utf-8 -*-
"""
Created on Wed Apr 01 16:32:57 2015

@author: Kaddabadda

join the csv files containing the precipitation sums for extreme periods (10min
hours, days etc) to the ZAMG station net shapefile

After the join, IDW to tif can be used to interpolate in space

"""

import os
import sys
import subprocess
import pandas as pd
import csv

path2shp = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\Station_net'
shapefile = '\ZAMG_stations.shp'


path2tbl = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Tables\Tables_of_extremes_samples_joins'
path2dest = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\ARCGIS\Shapes_extremes_p99_9'

# loop through all csv in directory
tables = []
dest = []
for root, _, files in os.walk(path2tbl):
    for f in files:
        if f.endswith('.csv'):
            fullpath = os.path.join(root,f)
            print fullpath
            tables.append(fullpath)
            ### name for destination shape file:
            shp = f[0:-4] + '.shp'
            shppath = os.path.join(path2dest,shp)
            dest.append(shppath)

for eachTable, eachDest in zip(tables, dest):
    cmd = 'saga_cmd table_tools 4 -TABLE_A:%s -TABLE_B:%s -RESULT:%s -ID_A:%s \
           -ID_B:%s' % (path2shp + shapefile, eachTable,
                        eachDest, 'synnr', 'synnr')
    os.system(cmd)

#     # change field type from string to integer
#    cmd2 = 'saga_cmd table_tools 7 -TABLE:%s -OUTPUT:%s -TYPE:11' % (path2dest
#            + eachDest, path2dest + eachDest2)
#    os.system(cmd2)
#tables = ['\DailySumsxtr_1H_p999.csv', '\DailySumsxtr_1H_p999.csv',
#          '\DailySumsxtr_1D_p999.csv', '\DailySumsxtr_3D_p999.csv',
#          '\HourlySumsxtr_10minp999.csv', '\HourlySumsxtr_1H_p999.csv',
#          '\HourlySumsxtr_1D_p999.csv', '\HourlySumsxtr_3D_p999.csv']

#dest = ['\shp_DailySumsxtr_10minp999.shp', '\shp_DailySumsxtr_1H_p999.shp',
#        '\shp_DailySumsxtr_1D_p999.shp', '\shp_DailySumsxtr_3D_p999.shp',
#        '\shp_HourlySumsxtr_10minp999.shp', '\shp_HourlySumsxtr_1H_p999.shp',
#        '\shp_HourlySumsxtr_1D_p999.shp', '\shp_HourlySumsxtr_3D_p999.shp']
#


