# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 19:46:13 2015

Split kdtree_fast into initialization and query taken from source below
* input: two dimensional x,y netCDF
* source link: http://nbviewer.ipython.org/github/Unidata/tds-python-workshop/blob/master/netcdf-by-coordinates.ipynb

* IDW interpolation from ZAMG SPARTACUS grid to SEA gauge locations
    - locate closest gridpoint 
    - calculate distances for 8 surrounding cells
    - use four closest neighbors for inverse distance weighting with power 1
    



@author: Kaddabadda
"""

import numpy as np
import pandas as pd
import xray
import netCDF4
from scipy.spatial import cKDTree
from geopy.distance import vincenty
from math import pi
from numpy import cos, sin
import arcpy
import os
'''input data:
* stationlist with lat, lon and altitude
* netCDF datasets of SPARTACUS tasmax
'''
# stations:
#stationlist = pd.read_csv(r'',
#                          )
# spartacus datasets
ds = xray.open_dataset(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\tx_1961_1969.nc')

ncfile = netCDF4.MFDataset(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\tx_1961_1969.nc',
                           'r')
ncfile.variables.keys()

#path to spartacus
spaPth = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS'


'''-------------------------------------------------------------------------'''
''' LOCATE CLOSTEST GRIDCELL TO STATION'''

class Kdtree_fast(object):
    def __init__(self, ncfile, latvarname, lonvarname):
        self.ncfile = ncfile
        self.latvar = self.ncfile.variables[latvarname]
        self.lonvar = self.ncfile.variables[lonvarname]        
        # Read latitude and longitude from file into numpy arrays
        rad_factor = pi/180.0 # for trignometry, need angles in radians
        self.latvals = self.latvar[:] * rad_factor
        self.lonvals = self.lonvar[:] * rad_factor
        self.shape = self.latvals.shape
        clat,clon = cos(self.latvals),cos(self.lonvals)
        slat,slon = sin(self.latvals),sin(self.lonvals)
        clat_clon = clat*clon
        clat_slon = clat*slon
        triples = list(zip(np.ravel(clat*clon), np.ravel(clat*slon), np.ravel(slat)))
        self.kdt = cKDTree(triples)

    def query(self,lat0,lon0):
        rad_factor = pi/180.0 
        lat0_rad = lat0 * rad_factor
        lon0_rad = lon0 * rad_factor
        clat0,clon0 = cos(lat0_rad),cos(lon0_rad)
        slat0,slon0 = sin(lat0_rad),sin(lon0_rad)
        dist_sq_min, minindex_1d = self.kdt.query([clat0*clon0,clat0*slon0,slat0])
        iy_min, ixx_min = np.unravel_index(minindex_1d, self.shape)
        return iy_min,ixx_min


ns = Kdtree_fast(ncfile,'latitude','longitude')


# exemplary one station, do this for each station
station_yx = [46.3086, 9.59919]

# ix, iy are the integer indices of the closest gridpoint
iy,ixx = ns.query(station_yx[0], station_yx[1])

print 'Closest gridcell at (lat, lon): ', ns.latvar[iy,ixx], ns.lonvar[iy,ixx]
print 'Distance to Station [m]: ', vincenty(station_yx, (ns.latvar[iy,ixx], ns.lonvar[iy,ixx]), ellipsoid='WGS-84').meters

D_1 = []
# calculate distane to all surrounding gridcells:
for ys in range(iy-1, iy+2):
    if ys < 0:
        # do not search for cells outside domain if cell is at the corner/side (index 0)
        continue
    for xs in range(ixx-1, ixx+2):
        if xs < 0:
            continue
        else:
            la, lo = ns.latvar[ys,xs], ns.lonvar[ys,xs]
            D = vincenty(station_yx, (la, lo), ellipsoid='WGS-84').meters
            D_1.append([ys, xs, D])
            print 'Distance gridcell to station [m]: ', D

DFrame = pd.DataFrame(D_1, columns=['iy', 'ixx', 'distance'])
Top4 = DFrame.sort(columns = 'distance')[0:4]
Top4.index = ['C1', 'C2', 'C3', 'C4']
Top4['weight'] = 1/Top4.distance

Top4Dict = {}
for ind in Top4.index.values:
    Test = ds.sel(y=int(Top4.ix[ind].iy), x=int(Top4.ix[ind].ixx)).to_dataframe()
    Top4Dict.update({ind: Test['tasmax']})
NeigborCells = pd.concat(Top4Dict, axis=1)    

#T_station = sum(Top4.exampleT/Top4.distance)/sum(Top4.weight)

# calculate Distances to surrounding grid cells and foward four closest:
# closest grid cells:

'''-------------------------------------------------------------------------'''
''' GEOREFERENCE SPARTACUS GRID FOR ELEVATION FROM DEM'''

''' for georeferening the dataset get
* source control points (y, x) and 
* target control points (lat, lon)
* format: "'0 1'; '0 2'"
          "'46.3 13.9'; '46.4 13.99'"
'''
sourcelist = []
targetlist = []
'''
* export grid cell lat and lon and save as csv
* use in GIS to extract elevation information for each point
'''
xyDATA = [] 
for iy in ds.y.values:
    for ixx in ds.x.values:
#        print 'Y: ', iy, '\n X: ', ixx
        source = "'" + str(ixx) + ' ' +  str(iy) +"'"
        sourcelist.append(source)
#        print source
        target ="'" + str(ns.lonvar[iy, ixx]) + ' ' + str(ns.latvar[iy, ixx])+"'"
        xyData = [ns.lonvar[iy, ixx], ns.latvar[iy, ixx]]
        xyDATA.append(xyData)
        targetlist.append(target)
#        print target

df = pd.DataFrame(xyDATA, columns=['x','y'])
df.to_csv(spaPth+'/xyDATA.csv')

source_points = ';'.join(sourcelist)
target_points = ';'.join(targetlist)

##====================================
##Warp
##Usage: Warp_management in_raster source_control_points;source_control_points... 
##                       target_control_points;target_control_points... out_raster
##                       {POLYORDER_ZERO | POLYORDER1 | POLYORDER2 | POLYORDER3 | 
##                       ADJUST | SPLINE | PROJECTIVE} {NEAREST | BILINEAR | 
##                       CUBIC | MAJORITY}
    
    

arcpy.env.workspace = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX'
#arcpy.env.cellSize = 1
arcpy.env.overwriteOutput = True
outWorkspace = arcpy.env.workspace

##Warp a TIFF raster dataset with control points
##Define source control points
source_pnt = source_points

##Define target control points
target_pnt = target_points

''' 
* input: tasmax_Layer1.tif was exported from NetCDF to Raster
'''
arcpy.Warp_management("tasmax_Layer1.tif",
                      source_pnt,
                      target_pnt,
                      "Spartacus", # no extension for ESRI grid
                      "POLYORDER1",
                      "CUBIC")












in_fc = "TEST2"
out_fc = "SPARTA_WGS"
# Set output coordinate system
outCS = arcpy.SpatialReference('WGS_1984_UTM_Zone_33N')
arcpy.Project_management(in_fc, out_fc, outCS)






try:
    # Use ListFeatureClasses to generate a list of inputs 
    for infc in arcpy.ListFeatureClasses():
    
        # Determine if the input has a defined coordinate system, can't project it if it does not
        dsc = arcpy.Describe(infc)
    
        if dsc.spatialReference.Name == "Unknown":
            print ('skipped this fc due to undefined coordinate system: ' + infc)
        else:
            # Determine the new output feature class path and name
            outfc = os.path.join(outWorkspace, infc)
            
            # Set output coordinate system
            outCS = arcpy.SpatialReference('NAD 1983 UTM Zone 11N')
            
            # run project tool
            arcpy.Project_management(infc, outfc, outCS)
            
            # check messages
            print(arcpy.GetMessages())
            
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])




ncfile.close()

# extracts the time series of T 

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''


# SEA bounds
lat_bnds, lon_bnds = [46.4036, 46.9802], [12.3406, 16.7288]

# closest grid cells:

# Difference in elevation:
z_Station = 100
z_Gridcell = 102
diff = z_Gridcell - z_Station

            