# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 19:46:13 2015

Split kdtree_fast into initialization and query taken from source below
* input: two dimensional x,y netCDF
* source link: http://nbviewer.ipython.org/github/Unidata/tds-python-workshop/blob/master/netcdf-by-coordinates.ipynb

* IDW interpolation from ZAMG SPARTACUS grid to SEA gauge locations
    - locate closest gridpoint 
    - calculate distances for 8 surrounding cells
    - infer mean elevation of gridcell from 10m DEM
    - correct temperatures for height diffs with lapse rate
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

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
'''GET POSITION XYZ OF ZAMG AND AHYD STATIONS '''
p = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data'
stations_AHYD = pd.read_csv(p + r'\AHYD\AHYD_shape_Export_LatLonDD.csv',
                            sep=';',
                            thousands=',',
                            usecols=[4,8,14,15],
                            skiprows=1,
                            header=None,
                            names=['STATNR', 'elev', 'lat', 'lon']
                            )
stations_ZAMG = pd.read_csv(p + r'\ZAMG\Shapefile_ZAMG_SEA_HiRes\ZAMG_SEA_DD.csv',
                            sep=';',
                            thousands=',',
                            usecols=[3,7,13,14],
                            skiprows=1,
                            header=None,
                            names=['STATNR', 'elev', 'lat', 'lon']
                            )
stations_ALL = pd.concat([stations_AHYD, stations_ZAMG],
                         ignore_index=True)      
stations_ALL.index = stations_ALL.STATNR 
                        
'''spartacus datasets'''
SPARTApath = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX'
SPARTAData = [r'\tx_1961_1969.nc',
              r'\tx_1970_1979.nc',
              r'\tx_1980_1989.nc',
              r'\tx_1990_1999.nc',
              r'\tx_2000_2011.nc']

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
''' PRELIMINARY ELEVATION FOR SPARTACUS CELLS INTERPOLATED FROM DEM
* read the csv file exported from GIS
* contains spartacus points around gauges (2km buffer) 
  and elevation information, indexed by interger x and y indices (iy and ixx)
  (netCDF dimensions)
* elevation: 10m Austria Lambert
    - transformed to WGS84
    - aggregated to 500m
    - value assigned to Spartacus cell by bilinear interpol 
      (4 nearest neighbors)
    '''
spaPth = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS'
SPARTA_elev = pd.read_csv(spaPth + '/XYBufferPoints_Elevation.csv',
            delim_whitespace=True,
            skipinitialspace=True,
            decimal=',',
            usecols=[3,4,5,6,7],
            na_values=-9999,
            skiprows=1,
            header=None,
            names=['ixx', 'iy', 'lon', 'lat','elev'])

'''-------------------------------------------------------------------------'''
''' LOCATE CLOSTEST GRIDCELL TO STATION'''

class Kdtree_fast(object):
    def __init__(self, ncfile, latvarname, lonvarname):
        self.ncfile = ncfile
        self.latvar = self.ncfile.variables[latvarname]
        self.lonvar = self.ncfile.variables[lonvarname] 
        self.SPARTA_elev = SPARTA_elev
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
    
    def fourNeighbors(self,lat0,lon0, z0):
        ''' FOUR CLOSEST GRIDCELLS TO INPUT lat0, lon0, z0 (station elev)
        * Out: Top4 
            - index integer
            - distance
            - IDW weight
            - time series
            - temperature lapse rate correction of neighbor gridcells
              based on elevation offset
        '''
        ''' locate closest gridcell to station (integer x and y indices)'''
        iy, ixx = self.query(lat0,lon0)
#            print iy
        D_1 = []
        '''calculate distance station - surrounding gridcells (index +-1):'''
        for ys in range(iy-1, iy+2):
#                print 'integer index lat/y: ', ys
            if ys < 0:
                '''do not search for cells outside domain if cell is at the corner/side (index 0)'''
                continue
            for xs in range(ixx-1, ixx+2):
#                    print 'integer index lon/x: ',xs
                if xs < 0:
                    continue
                else:
                    '''lat and lon of each of the neighbor cells'''
                    la, lo = self.latvar[ys,xs], self.lonvar[ys,xs]
                    '''distance of each spartacus cell to station lat/lon'''
                    D = vincenty((lat0, lon0), (la, lo), ellipsoid='WGS-84').meters
                    '''elevation of the spartacus gridcell'''
                    EleVal = self.SPARTA_elev['elev'][np.logical_and(SPARTA_elev.ixx==xs, SPARTA_elev.iy==ys)]
                    if EleVal.empty is True:
                        print 'no elevation value'
                        z = np.nan
                        dT = np.nan
                        D_1.append([ys, xs, D, z, dT])
                    else: 
                        z = float(EleVal.values)
                        dT = (z0 - z)*0.0065
                        D_1.append([ys, xs, D, z, dT])
       
        DFrame = pd.DataFrame(D_1, columns=['iy', 'ixx', 'distance',
                                            'elevation', 'Tcorrection'])
        '''write four closest gridcells in DataFrame'''
        Top4 = DFrame.sort(columns = 'distance')[0:4]
        Top4.index = ['C1', 'C2', 'C3', 'C4']
        '''calculate weight by simple inverse distance'''
        Top4['weight'] = 1/Top4.distance
        
        '''get tasmax series of four neighbors'''
        Top4Dict = {}
        for Cell in Top4.index.values:
            '''get tasmax series of integer indices x and y'''
            CellTasmax = ds.sel(y=int(Top4.ix[Cell].iy), x=int(Top4.ix[Cell].ixx)).to_dataframe()
            '''transfer tasmax from Cell elevation to station elevation'''
            if Top4.ix[Cell].Tcorrection is np.nan:
                CellTasmaxCorr = CellTasmax
                print 'no elevation correction possible, using uncorrected'
            else:
                CellTasmaxCorr = CellTasmax + Top4.ix[Cell].Tcorrection
            Top4Dict.update({Cell: CellTasmaxCorr['tasmax']})
        NeighborCells = pd.concat(Top4Dict, axis=1)  
        '''temperature lapse rate correction factor'''
        return Top4, NeighborCells
'''-------------------------------------------------------------------------
GET TASMAX TIME SERIES FOR EVERY STATION THROUGH IDW BASED ON FOUR 
NEAREST NEIGHBORS
-------------------------------------------------------------------------'''
for decade in SPARTAData[1:]:
    print 'processing', decade
    ds = xray.open_dataset(SPARTApath + decade)
    ncfile = netCDF4.MFDataset(SPARTApath + decade, 'r')
    ''' instance for finding closest cell'''
    ns = Kdtree_fast(ncfile,'latitude','longitude')
    tempDict = {}
    for i, station in enumerate(stations_ALL.index):  
        print 'processing station', int(station), '\n', i+1, 'out of', len(stations_ALL.index)
        StatLat = stations_ALL.ix[station].lat
        StatLon = stations_ALL.ix[station].lon
        z0 = stations_ALL.ix[station].elev
        '''get 4 closest neighbors, distance, weight and elevation-corrected
        temperature series'''
        Top4, Top4tasmax = ns.fourNeighbors(StatLat, StatLon, z0)
        '''IDW
        wanted = sum(knownValues/distance)/sum(weight)'''
        firstPart = Top4tasmax.divide(Top4.distance.values).sum(axis=1)
        EstTasmaxStation = firstPart.divide(sum(Top4.weight))
        tempDict.update({station: EstTasmaxStation})
    StationTasmaxSpartaIDW = pd.concat(tempDict, axis=1)
    StationTasmaxSpartaIDW.to_pickle(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\StationTasmaxIDW\IDW_' + decade[1:-3] + '.npy')
    ncfile.close()
    
    #    # integer indices of the closest gridpoint:
    #    iy,ixx = ns.query(StatLat, StatLon)
    #    print 'Closest gridcell at (lat, lon): ', ns.latvar[iy,ixx], ns.lonvar[iy,ixx]
    #    print 'Distance to Station [m]: ', vincenty((StatLat, StatLon), (ns.latvar[iy,ixx], ns.lonvar[iy,ixx]), ellipsoid='WGS-84').meters

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''   
''' SAVE TASMAX DATAFRAME ALL STATION SERIES'''      
dirSPARTA = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX\StationTasmaxIDW'

decades = [['61-69', [1961, 1969]],
           ['70-79', [1970, 1979]],
           ['80-89', [1980, 1989]],
           ['90-99', [1990, 1999]],
           ['00-11', [2000, 2011]]]
#           ['12-14', [2012, 2014]]]
DecDict = {}
for decade in decades:
    infile = dirSPARTA + r'\IDW_tx_' + str(decade[1][0]) + '_' + str(decade[1][1]) + '.npy'
    decadeTasmax = pd.read_pickle(infile)
    DecDict.update({decade[0]: decadeTasmax})

FrameALL = pd.concat(DecDict, axis=0)
FrameALL.index = FrameALL.index.get_level_values(1)
FrameALL.sort_index(inplace=True)
FrameALL.to_pickle(dirSPARTA + '\StationSeries\IDW_tasmax_ALLstations.npy')
''' if wanted, save single files for each station'''
for station in FrameALL.columns.values:
    StationSeries = FrameALL[station]
    StationSeries.to_pickle(dirSPARTA + '\StationSeries\IDW_tasmax_' + str(station) + '.npy')

'''-------------------------------------------------------------------------'''
''' WRITE CELL LAT LON TO POINT FILE (for processing in GIS) '''
'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
def gridpoints_to_CSV(xrayDS):
    ''' for georeferening the SPARTACUS dataset:
    * INPUT: xray dataset of SPARTACUS netCDF with dimesions x,y and lat(y,x) and lon(y,x)
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
            target ="'" + str(ds['longitude'].sel(x=ixx, y=iy).values) + ' ' + str(ds['latitude'].sel(x=ixx, y=iy).values)+"'"
            # Lat Lon identification for all            
            xyData = [int(ixx), int(iy), ds['longitude'].sel(x=ixx, y=iy).values, ds['latitude'].sel(x=ixx, y=iy).values]
            xyDATA.append(xyData)
            targetlist.append(target)
    #        print target
    
    ''' Save all x,y to get elev info for each x,y (bilinear from 500m DEM)'''
    df = pd.DataFrame(xyDATA, columns=['x','y', 'lat', 'lon'])
    df.to_csv(spaPth+'/xyDATA.csv')

    source_points = ';'.join(sourcelist)
    target_points = ';'.join(targetlist)
    return source_points, target_points
'''-------------------------------------------------------------------------'''
''' GEOREFERENCE SPARTACUS GRID FOR ELEVATION FROM DEM
* input: tasmax_Layer1.tif was exported from NetCDF to Raster
* sourcepoints are the integer indices of the NetCDF (x and y from 1-N)
* targetpoints are the (lat/lon) for each (y,x) pair
'''
arcpy.env.workspace = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\SPARTACUS\TMAX'
#arcpy.env.cellSize = 1
arcpy.env.overwriteOutput = True
outWorkspace = arcpy.env.workspace
source_points,target_points =  gridpoints_to_CSV(ds)

arcpy.Warp_management("tasmax_Layer1.tif",
                      source_points,
                      target_points,
                      "Spartacus", # no extension for ESRI grid
                      "POLYORDER1",
                      "CUBIC")
         