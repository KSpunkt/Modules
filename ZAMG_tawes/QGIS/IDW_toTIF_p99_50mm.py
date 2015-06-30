# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 12:02:31 2015

@author: Kaddabadda

loops through atttribute table of input shapefile
and performs an interpolation algorithm in SAGA GIS and exports to tif
format
"""

import os
import sys
import subprocess
import pandas as pd
import csv

path2shp = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\allDays2'
shapefile = '\ZAMG_stations_p99_50mm.shp'
fields = range(10,58)  # attribute field numbers in SAGA (SAGA table description)

path2dest = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\QGIS\Interpolation\daily_p99_50mm'

# read fieldnames (= dates of events)
csvpth = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\allDays2\allDailySums.csv'
with open(csvpth, 'r') as cfile:
    fieldnames = csv.reader(cfile).next()
    del fieldnames[0]


for eachField in fields:
    i = eachField-10  # for naming the tifs with date of event
    print 'processing field: ', eachField, 'date: ', fieldnames[i]
    # IDW (6 nearest points) for each column in attribute table
    cmd = 'saga_cmd grid_gridding 1 -SHAPES:%s -FIELD:%s -SEARCH_RANGE:%s \
     -SEARCH_RADIUS:%s -SEARCH_POINTS_MAX:%s -TARGET_USER_SIZE:%s -TARGET_OUT_GRID:%s' \
        % (path2shp + shapefile, eachField, 1, 10000, 6, 100,  path2dest +
           '/IDW_' + str(eachField))
    os.system(cmd)
    # converts saga grid to tif
    cmd2 = 'saga_cmd io_gdal 2 -GRIDS:%s -FILE:%s' % (path2dest + '/IDW_'
                                                      + str(eachField) +
                                                      '.sgrd', path2dest +
                                                      '/IDW' + str(fieldnames[i])
                                                    + '.tif')
    os.system(cmd2)

    print '/IDW' + str(fieldnames[i])+ '.tif  created'







