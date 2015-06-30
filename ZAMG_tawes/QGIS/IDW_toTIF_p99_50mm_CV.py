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
import shutil

path2shp = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\allDays2'
shapefile = '\ZAMG_stations_p99_50mm.shp'
fields = range(10,61)  # attribute field numbers in SAGA (SAGA table description)


path2dest = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\QGIS\Interpolation\CrossVal'
path2dest2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\QGIS\Interpolation\CrossVal\CV_differences_per_run\shapes'
path2dest3 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\QGIS\Interpolation\CrossVal\CV_differences_per_run\tables'


# read fieldnames (= dates of events)
csvpth = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\allDays\allDailySums.csv'
with open(csvpth, 'r') as cfile:
    fieldnames = csv.reader(cfile).next()
    del fieldnames[0]

# do the interpolation for 90% of the stations
for eachField in fields:
    os.mkdir(path2dest2)
    i = eachField-10  # for naming the tifs with date of event
    print 'processing field: ', eachField, 'date: ', fieldnames[i]
    # split the station shapefile in 90% and 10% randomly
    cmd3 = 'saga_cmd shapes_tools 16 -SHAPES:%s -A:%s -B:%s -PERCENT:%s -EXACT:1' \
           % (path2shp + shapefile, path2dest2 + '\CV_A' + str(eachField) +
              '.shp', path2dest2 + '\CV_B' + str(eachField) + '.shp', 10.0)
    os.system(cmd3)

    # IDW (6 nearest points) for 90% of shapes in attribute table
    cmd = 'saga_cmd grid_gridding 1 -SHAPES:%s -FIELD:%s -SEARCH_RANGE:%s \
     -SEARCH_RADIUS:%s -SEARCH_POINTS_MAX:%s -TARGET_USER_SIZE:%s -TARGET_OUT_GRID:%s' \
        % (path2dest2 + '\CV_A' + str(eachField) + '.shp', eachField, 1, 10000, 6, 100,  path2dest +
           '/IDW_' + str(eachField))
    os.system(cmd)
    print 'interpolating training sample ...'
    # converts saga grid to tif
    cmd2 = 'saga_cmd io_gdal 2 -GRIDS:%s -FILE:%s' % (path2dest + '/IDW_'
                                                      + str(eachField) +
                                                      '.sgrd', path2dest +
                                                      '/IDW' + str(fieldnames[i])
                                                    + '.tif')
    os.system(cmd2)

    print '/IDW' + str(fieldnames[i])+ '.sgrd  created'

    # get the interpolated value for the residual 10% of the stations and calculate
    # error

    # Add interpolated value to attribute table
    cmd4 = 'saga_cmd shapes_grid 0 -SHAPES:%s -GRIDS:%s' \
           % (path2dest2 + '\CV_B' + str(eachField) + '.shp', path2dest + '/IDW_' + str(eachField) + '.sgrd')
    os.system(cmd4)
    # calculate difference of interpolated and measured value
    cmd5 = 'saga_cmd table_calculus 2 -FORMULA:%s -NAME:%s -TABLE:%s' \
           % ('[IDW_' + str(eachField) + ']-f' + str(eachField), 'DF_' + str(eachField), path2dest2 + '\CV_B' + str(eachField) + '.shp')
    os.system(cmd5)
    print 'calculating validation sample...'
    # select diff field
    cmd6 = 'saga_cmd table_tools 19 -TABLE:%s -FIELD:%s' % (path2dest2 + '\CV_B' + str(eachField) + '.shp', 'DF_' + str(eachField))
    os.system(cmd6)
    # export table with result for day x
    cmd7 = 'saga_cmd io_table 0 -TABLE:%s -HEADLINE:1 -SEPARATOR:%s -FILENAME:%s' \
           % (path2dest2 + '\CV_B' + str(eachField) + '.shp', 2, path2dest3 + '/RES_' + str(fieldnames[i]) + '.csv')

    os.system(cmd7)
    print 'results saved in table.'
    #os.rmdir(path2dest2)
    shutil.rmtree(path2dest2)

''' read CSV Files, field DF_field_number to get mean error of each interpolation
Absolute Error Cross Validation
'''
AECV = pd.DataFrame()
for eachField, i in zip(fields, range(len(fieldnames))):
    print 'read ', eachField
    aecv = pd.io.parsers.read_csv(path2dest3 + '/RES_' + str(fieldnames[i]) + '.csv',
                           usecols=['DF_'  + str(eachField)])
    print aecv
    print aecv.mean()
    AECV = pd.concat([AECV, aecv], ignore_index=True, axis=1)

AECV.to_csv(r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\QGIS\Interpolation\CrossVal\CV_differences_per_run\AbsError_CV.csv')