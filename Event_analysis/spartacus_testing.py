# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 19:46:13 2015

@author: Kaddabadda
"""

import numpy as np
import pandas as pd
import xray
import netCDF4
from scipy.spatial import distance, cKDTree
from geopy.distance import vincenty
from math import pi
from numpy import cos, sin

# stations:
stationlist = pd.read_csv(r'',
                          )

# spartacus datasets
ds = xray.open_dataset(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\tx_1961_1969.nc')

ncfile = netCDF4.MFDataset(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\tx_1961_1969.nc',
                           'r')
ncfile.variables.keys()


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
''' Split kdtree_fast into initialization and query
* input: two dimensional x,y netCDF

*source link:
http://nbviewer.ipython.org/github/Unidata/tds-python-workshop/blob/master/netcdf-by-coordinates.ipynb
'''

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
        iy_min, ix_min = np.unravel_index(minindex_1d, self.shape)
        return iy_min,ix_min


ns = Kdtree_fast(ncfile,'latitude','longitude')


# for each station
station_yx = [46.3086, 9.59919]

# ix, iy are the integer indices of the closest gridpoint
iy,ix = ns.query(station_yx[0], station_yx[1])

print 'Closest gridcell at (lat, lon): ', ns.latvar[iy,ix], ns.lonvar[iy,ix]
print 'Distance to Station [m]: ', vincenty(station_yx, (ns.latvar[iy,ix], ns.lonvar[iy,ix]), ellipsoid='WGS-84').meters

D_1 = []
# calculate distane to all surrounding gridcells:
for i in range(iy-1, iy+2):
    if i < 0:
        continue
    for j in range(ix-1, ix+2):
        if j < 0:
            continue
        else:
            la, lo = ns.latvar[i,j], ns.lonvar[i,j]
            D = vincenty(station_yx, (la, lo), ellipsoid='WGS-84').meters
            D_1.append([i, j, D])
            print 'Distance gridcell to station [m]: ', D

DFrame = pd.DataFrame(D_1, columns=['iy', 'ix', 'distance'])
Top4 = DFrame.sort(columns = 'distance')[0:4]
Top4['weight'] = 1/Top4.distance

# values at the closest gridpoints:
Top4['exampleT'] = [1, 100, 200, 100]

T_station = sum(Top4.exampleT/Top4.distance)/sum(Top4.weight)

# calculate Distances to surrounding grid cells and foward four closest:
# closest grid cells:


ncfile.close()

# extracts the time series of T 
SerClosestPoint = ds.tasmax[:, iy-1:iy+1, ix-1:ix+1].to_dataframe()

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''

# lats and lons are twodimensional because its a regular 1km resolution and not
# on a regular lat/lon grid
#12.3406, 16.7288
lats = f.variables['latitude'][:] # this is a matrix not an array
lons = f.variables['longitude'][:]

# SEA bounds
lat_bnds, lon_bnds = [46.4036, 46.9802], [12.3406, 16.7288]

lat_inds = np.where((lats > lat_bnds[0]) & (lats < lat_bnds[1]))
lon_inds = np.where((lons > lon_bnds[0]) & (lons < lon_bnds[1]))

SEA_subset = f.variables['tasmax'][:,lat_inds,lon_inds]

SEA_subset = f.variables['tasmax'][:,[4,6],[4,6]]

# only search in vicinity of station: (1km grid (0.001 rad))

day = ds.sel(time=slice('1962-10-01', '1962-10-01'), x=48)

                  
''''''     
   



# closest grid cells:
vincenty(station_xy, grid_cell, ellipsoid='WGS-84').meters

# Difference in elevation:
z_Station = 100
z_Gridcell = 102
diff = z_Gridcell - z_Station

            