# -*- coding: utf-8 -*-
"""
Created on Tue Jun 09 14:43:29 2015

@author: Kaddabadda
make plot where Intensity is colored x axis is time and Y latitude/lon
of stations
"""
import matplotlib as mpl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import *
from scipy import mgrid
import matplotlib.dates as mdates
import datetime as dt

colors = ['#ffffff', '#add8e6', '#4169e1', '#ee82ee', '#b03060', '#ff1493']
cmap = matplotlib.colors.ListedColormap(colors, name=u'precip', N=None)
#cmap.norm.clip = False
#cmap.set_under('white')

bounds = [0, 0.1, 0.5, 1.7, 8.3, 17, 30]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
vmin= 0
vmax= 30

## minimum values for colorbar. filter our nans which are in the grid
#zmin    = grid[np.where(np.isnan(X) == False)].min()
#zmax    = grid[np.where(np.isnan(X) == False)].max()

def event_matrix(event, orientation, filename):
    '''
    draw an intensity matrix for an
    *** event [pandas dataframe]
    plot where stations are either sorted by latitide (N-S):
    orientation: 1
    or longitude (W-E):
    orientation: 2
    '''
    path = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG'
    plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_heatmaps'

    # read stationlist to order stations by lat and lon
   
    if orientation==1:
        print 'Drawing intensity matrix North-South'
        sortfile = '\ZAMG_stations_SW_Alps_150216_sorted_lat_lon.csv'
        # make array where first column is northernmost station (2nd order west)
        station_order = pd.read_csv(path+sortfile, sep=';', usecols=[0,1],
                                            dtype='str')
        
        # preallocate station x time array
        event_intenisty_matrix = np.empty((len(station_order),len(event)))
        # fill intensities into array  
        for eachStation, i in zip(station_order['synnr'].values,
                                  range(len(station_order['synnr'].values))):
            data = event[eachStation].values
            event_intenisty_matrix[i,:] = data
        X = event_intenisty_matrix
        #### ----------- 
        ## PLOT
        #### -----------        
        fig, [ax, ax1] = plt.subplots(1,2,  figsize=(11, 8))
        fig.suptitle("Precipitation Intensity North-South", fontsize=14)
        fig.set_facecolor('#d3d3d3')
#        ax = plt.subplot(1,14,(1,13))
#        ax.set_title("Precipitation Intensity N-S", fontsize=14)
        ax.set_aspect('auto')
        ax.set_position((0.1, 0.1, .65, .8))
        x_lims = [event.index.to_pydatetime()[0], event.index.to_pydatetime()[-1]]
        x_lims = mdates.date2num(x_lims)
        y_lims = [0, 79]
        ax.imshow(X, interpolation='nearest',
                        extent = [x_lims[0], x_lims[1],  y_lims[0], y_lims[1]],
                        cmap=cmap, norm=norm, origin='lower', aspect='auto', 
                        vmin=vmin, vmax=vmax) #aspect='auto') 
        #plt.colorbar(im, orientation='vertical')

        ax.patch.set_facecolor('grey')
        # ---- X AXIS PROPERTIES ----
#        ax.xaxis.grid(True, which="minor")   
    #    ax.xaxis_date()
        ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=(0),
                                                        interval=1))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M\n%d.%b'))
        ax.xaxis.grid(True, which="minor")
        ax.xaxis.grid()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('\n\n\n%Y'))    
        
        # ---- Y AXIS PROPERTIES ----
        ax.set_ylabel('S <-- stations (sorted by latitude) --> N', fontsize=10)      
        #plt.yticks(arange(79), station_order['synnr'].values, fontsize=10)
        ax.yaxis.set_ticks(arange(79))
        ax.set_yticklabels(station_order['synnr'].values, fontsize=6) 
        # ------- COLORBAR ------
        #ax1 = plt.subplot(1,15,15)
        ax1.set_aspect('auto')
        ax1.set_position((.85, .1, .05, .8))
        cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm,
                             # to use 'extend', you must
                             # specify two extra boundaries:
                             boundaries=[-1]+bounds+[5],
                             extend='both',
                             ticks=bounds, # optional
                             spacing='proportional',
                             orientation='vertical')
#        mpl.colorbar.make_axes_gridspec(ax1, fraction=.9)     
        cmap.set_over('#adff2f')
        #cb2.set_label('')
        #cb2.set_ticklabels([])
        cb2.ax.tick_params(axis='y', direction='in') 
        cb2.ax.set_yticklabels(['', '', '0.5' , '1.7', '8.3','17', '30'],
                               fontsize=10, rotation=0) 
        ax1.text(-.25, .75, 'torrential', fontsize=8, rotation=0, ha='right')
        ax1.text(-.25, .4, 'very \n heavy', fontsize=8, rotation=0, ha='right')
        ax1.text(-.25, .14, 'heavy', fontsize=8, rotation=0, ha='right')  
        ax1.text(-.25, .035, 'moderate', fontsize=8, ha='right')  
        ax1.text(-.25, -.01, 'light', fontsize=8, rotation=0, ha='right')                        
        ax1.text(.5, 1.1, 'mm/10min', fontsize=8, rotation=0, ha='right',
                 weight='bold')  
        
        savefig(plotpath+'/'+filename, dpi=300, facecolor=fig.get_facecolor(),
                edgecolor='none')
        close(fig)
      
    else:
        print 'Drawing intensity matrix West-East'
        sortfile = '\ZAMG_stations_SW_Alps_150216_sorted_lon_lat.csv'
         # make array where first column is northernmost station (2nd order west)
        station_order = pd.read_csv(path+sortfile, sep=';', usecols=[0,1],
                                            dtype='str')
        
        # preallocate station x time array
        event_intenisty_matrix = np.empty((len(event), len(station_order)))
        # fill intensities into array  
        for eachStation, i in zip(station_order['synnr'].values,
                                  range(len(station_order['synnr'].values))):
            data = event[eachStation].values
            event_intenisty_matrix[:,i] = data   
        X = event_intenisty_matrix
        
        #### ----------- 
        ## PLOT
        #### -----------
        
        fig, [ax, ax1] = plt.subplots(1,2,  figsize=(8, 11))
        fig.suptitle("Precipitation Intensity West-East", fontsize=14)
        fig.set_facecolor('#d3d3d3')
        ax.set_aspect('auto')
        ax.set_position((0.1, 0.1, .65, .8))
        y_lims = [event.index.to_pydatetime()[0], event.index.to_pydatetime()[-1]]
        y_lims = mdates.date2num(y_lims)
        x_lims = [0, 79]
        
        # ---------------------
        ax.imshow(X, interpolation='nearest',
                        extent = [x_lims[0], x_lims[1],  y_lims[0], y_lims[1]],
                        cmap=cmap, norm=norm, origin='lower', aspect='auto', 
                        vmin=vmin, vmax=vmax) #aspect='auto') 
        # ---------------------
                        
        # plt.colorbar(im, orientation='vertical')
        ax.patch.set_facecolor('gray')
        
        # ---------------------
        # ---- X AXIS PROPERTIES ----
        # ---------------------
#        ax.yaxis.grid(True, which="minor")   
    #    ax.xaxis_date()
        ax.yaxis.set_minor_locator(mdates.HourLocator(byhour=(0),
                                                        interval=1))
        ax.yaxis.set_minor_formatter(mdates.DateFormatter('%H:%M\n%d.%b'))
        ax.yaxis.grid(True, which="minor")
        ax.yaxis.grid()
        ax.yaxis.set_major_locator(mdates.MonthLocator())
        ax.yaxis.set_major_formatter(mdates.DateFormatter('\n\n\n%Y'))    
        
        # ---------------------
        # ---- Y AXIS PROPERTIES ----
        # ---------------------
        ax.set_xlabel('W <-- stations (sorted by longitude) --> E', fontsize=10)      
#        plt.xticks(arange(79), station_order['synnr'].values, fontsize=5)
#        plt.setp(ax.get_xticklabels(), rotation=90)
        ax.xaxis.set_ticks(arange(79))
        ax.set_xticklabels(station_order['synnr'].values, fontsize=6, rotation=90) 
        
        # ---------------------
        # ------- COLORBAR ----
        # ---------------------
        ax1.set_aspect('auto')
        ax1.set_position((.85, .1, .05, .8))
        cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm,
                             # to use 'extend', you must
                             # specify two extra boundaries:
                             boundaries=[-1]+bounds+[5],
                             extend='both',
                             ticks=bounds, # optional
                             spacing='proportional',
                             orientation='vertical')
#        mpl.colorbar.make_axes_gridspec(ax1, fraction=.9)     
        cmap.set_over('#adff2f')
        #cb2.set_label('')
        #cb2.set_ticklabels([])
        cb2.ax.tick_params(axis='y', direction='in') 
        cb2.ax.set_yticklabels(['', '', '0.5' , '1.7', '8.3','17', '30'],
                               fontsize=10, rotation=0) 
        ax1.text(-0.25, .75, 'torrential', fontsize=8, rotation=0, ha='right')
        ax1.text(-0.25, .4, 'very \n heavy', fontsize=8, rotation=0, ha='right')
        ax1.text(-0.25, .14, 'heavy', fontsize=8, rotation=0, ha='right')  
        ax1.text(-0.25, .035, 'moderate', fontsize=8, ha='right')  
        ax1.text(-0.25, -.01, 'light', fontsize=8, rotation=0, ha='right')                        
        ax1.text(.5, 1.1, 'mm/10min', fontsize=8, rotation=0, weight='bold')  

        savefig(plotpath+'/'+filename, dpi=300, facecolor=fig.get_facecolor(),
                edgecolor='none')
        close(fig)
    
