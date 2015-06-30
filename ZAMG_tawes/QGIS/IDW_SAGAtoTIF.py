# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 12:02:31 2015

@author: Kaddabadda

starts a GRASS session, loops through atttribute table of input shapefile
and performs an interpolation algorithm in SAGA GIS and exports to tif
format
"""

# initialize grass session


import os
import sys
import subprocess
# import GRASS Python bindings (see also pygrass)
import grass.script as grass
import grass.script.setup as gsetup

sagapath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\SAGA\IDW_98'
resultpth = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\SAGA\IDW_98\tif'
qgispath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\QGIS'
grasspth = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\GRASS'

# GISBASE SE Alpine Region (bounding Box of ZAMG stations), coordinate System UTM Z33N
gisbase = os.environ['GISBASE']
gisdbase = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\GRASS\Austria'
location = "SE_Alpine"
mapset   = "ZAMG_SE_Alpine"
gsetup.init(gisbase, gisdbase, location, mapset)
print grass.gisenv()

grass.message('Current GRASS GIS 7 environment:')
print grass.gisenv()

grass.message('Available raster maps:')
for rast in grass.list_strings(type = 'rast'):
    print rast

grass.message('Available vector maps:')
for vect in grass.list_strings(type = 'vect'):
    print vect


AttrTable = range(12,440) # fields in attribute table containing precip [mm]

for eachField in AttrTable:
    # IDW (6 nearest points) for each column in attribute table
    cmd = 'saga_cmd grid_gridding 1 -SHAPES:%s -FIELD:%s -SEARCH_RANGE:%s \
     -SEARCH_RADIUS:%s -SEARCH_POINTS_MAX:%s -USER_SIZE:%s -USER_GRID:%s' \
        % (qgispath + '\ZAMG_UTM33_98daily.shp', eachField, 1, 10000, 6, 100,  sagapath + '/IDW_' + str(eachField))
    os.system(cmd)
    # converts saga grid to tif
    cmd2 = 'saga_cmd io_gdal 2 -GRIDS:%s -FILE:%s' % (sagapath + '/IDW_' + str(eachField) + '.sgrd', resultpth + '/IDW' + str(eachField) + '.tif')
    os.system(cmd2)
    # imports tif rater to GRASS mapset
    grass.run_command('r.in.gdal', input=resultpth + '/IDW' + str(eachField) + '.tif', output='idw_' str(eachField))

# set region to zone of rater maps
grass.parse_command('g.region', raster = 'idw' + str(eachField))

# r.out.mpeg doesnt work because mpeg ff libarary is not found... where to include/install/compile??
        grass.run_command('r.out.mpeg', view1='idw*', qual=5)







