# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:04:11 2015

@author: Kaddabadda
"""
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from itertools import izip

path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description\Plots'

''' IMPORT RAW DATA
'''
AHYD_all_stations = pd.read_pickle(src + '\AHYD_dailysums.npy')
ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min_allyear.npy')

# Mariapfarr crazy Rain
ZAMG_all_stations['11348']['19970703'].loc[ZAMG_all_stations['11348']['19970703']>30] = np.nan
ZAMG_all_stations['11348']['19970704'].loc[ZAMG_all_stations['11348']['19970704']>30] = np.nan
ZAMG_all_stations['11265']['20060802'].loc[ZAMG_all_stations['11265']['20060802']>50] = np.nan

import Modules.Event_analysis.Event_statistics as es
'''
Create Eventframe instance to analyze datasets (percent of NaN per event are
calculated independent of required valid numbers for resampling )
'''
ZAMG_JJA = es.Eventframe(ZAMG_all_stations, resolution='10min', season=[6,8])

'''Get wet day and wet hour events in station dataframe'''                  
Dayframe = ZAMG_JJA.EventDays('ZAMG_10min_JJA') 
Hourframe = ZAMG_JJA.EventHours(Dayframe, 'ZAMG_10min_JJA')       

'''get the maximum numbers of the event based statistics'''
Dayframe.xs('max daily', level=1, axis=1).max(axis=1).order(ascending=False)


peaks_1_top50 = Dayframe.xs('peak 1', level=1, axis=1).max(axis=1).order(ascending=False)[0:51]
durations_D_top50 = Dayframe.xs('duration', level=1, axis=1).max(axis=1).order(ascending=False)[0:51]


''' Max value for axes in plot'''
peak1_D = Dayframe.xs('peak 1', level=1, axis=1).max().max()
duration_D = Dayframe.xs('duration', level=1, axis=1).max().max()

peak1_H = Hourframe.xs('peak 1', level=1, axis=1).max().max()
duration_H = Hourframe.xs('duration', level=1, axis=1).max().max()


plt.plot(Dayframe[station].index.month, Dayframe[station]['duration'].values,
             marker='x', linestyle='', color='red')

'''----------------------------------------------------------------------------
#### ----------- 
## PLOT
#### -----------    
----------------------------------------------------------------------------'''    
fig, [[ax, ax1], [ax2, ax3]] = plt.subplots(2,2,  figsize=(13, 10))
fig.suptitle("Day Events ZAMG 10min, JJA", fontsize=12)
''' Event duration against high resolution peaks '''
for station in Dayframe.columns.get_level_values(0):
    ax.plot(Dayframe[station].duration.values, Dayframe[station]['peak 1'].values,
             marker='x', linestyle='', color='red')
    ax.plot(Dayframe[station].duration.values, Dayframe[station]['peak 2'].values,
             marker='x', linestyle='', color='orange')
    ax.plot(Dayframe[station].duration.values, Dayframe[station]['peak 3'].values,
             marker='x', linestyle='', color='yellow')         
    ax.set_xlim([0, 30])# duration_H])
    ax.set_ylim([0, 60])# peak1_D])
    ax.grid(which='major')
    ax.set_ylabel('peaks (1st, 2nd, 3rd) [mm/10min]', fontsize=8) 
    ax.set_xlabel('event duration [consecutive wet days (>2mm)]', fontsize=8) 
    #ax.set_yscale('log')
    
    ''' Event duration against daily maxima '''
    ax1.plot(Dayframe[station].duration.values, Dayframe[station]['max daily'].values,
             marker='x', linestyle='', color='red')        
#    ax1.set_xlim([0, 30])# duration_H])
#    ax1.set_ylim([0, 60])# peak1_D])
    ax1.grid(which='major')
    ax1.set_ylabel('max day [mm/d]', fontsize=8) 
    ax1.set_xlabel('event duration [consecutive wet days (>2mm)]', fontsize=8) 
    #ax1.set_yscale('log')
    
    ''' Event duration against hourly maxima ''' 
    ax2.plot(Dayframe[station].duration.values, Dayframe[station]['max h 1'].values,
             marker='x', linestyle='', color='red')
    ax2.plot(Dayframe[station].duration.values, Dayframe[station]['max h 2'].values,
             marker='x', linestyle='', color='orange')      
#    ax2.set_xlim([0, 30])# duration_H])
#    ax2.set_ylim([0, 60])# peak1_D])
    ax2.grid(which='major')
    ax2.set_ylabel('max hourly (1st, 2nd) [mm/h]', fontsize=8) 
    ax2.set_xlabel('event duration [consecutive wet days (>2mm)]', fontsize=8) 
    #ax2.set_yscale('log')      

    ''' Event duration against hourly maxima '''    
    ax3.plot(Dayframe[station].duration.values, Dayframe[station]['mean rain rate'].values,
             marker='x', linestyle='', color='red')    
#    ax3.set_xlim([0, 30])# duration_H])
#    ax3.set_ylim([0, 60])# peak1_D])
    ax3.grid(which='major')
    ax3.set_ylabel('mean rain rate [mm/d]', fontsize=8) 
    ax3.set_xlabel('event duration [consecutive wet days (>2mm)]', fontsize=8) 
    #ax3.set_yscale('log') 

fig.savefig(plotpath+'/'+ 'DayEvents_ZAMG10min_JJA', dpi=300)
                
fig, [[ax, ax1], [ax2, ax3]] = plt.subplots(2,2,  figsize=(13, 10))
fig.suptitle("Hour Events ZAMG 10min, JJA", fontsize=12)
    
for [i, station] in enumerate(Hourframe.columns.get_level_values(0)):
    ax.plot(Hourframe[station].duration.values, Hourframe[station]['peak 1'].values,
             marker='x', linestyle='', color='red')
    ax.plot(Hourframe[station].duration.values, Hourframe[station]['peak 2'].values,
             marker='x', linestyle='', color='orange')
    ax.plot(Hourframe[station].duration.values, Hourframe[station]['peak 3'].values,
         marker='x', linestyle='', color='yellow')
    ax.set_xlim([0, 80])#duration_H])
    ax.set_ylim([0, 60])#peak1_H])
    ax.set_ylabel('[mm/10min]', fontsize=8) 
    ax.set_xlabel('event duration [consecutive wet hours (>.2mm)]', fontsize=8) 
    
    ''' Event duration against hourly maxima '''
    ax1.plot(Hourframe[station].duration.values, Hourframe[station]['max hourly'].values,
             marker='x', linestyle='', color='red')        
#    ax1.set_xlim([0, 30])# duration_H])
#    ax1.set_ylim([0, 60])# peak1_D])
    ax1.grid(which='major')
    ax1.set_ylabel('max day [mm/d]', fontsize=8) 
    ax1.set_xlabel('event duration [consecutive wet hours (>.2mm)]', fontsize=8) 
    #ax1.set_yscale('log')
    
    ''' Event duration against hourly maxima ''' 
    ax2.plot(Hourframe[station].duration.values, Hourframe[station]['sum'].values,
             marker='x', linestyle='', color='red') 
#    ax2.set_xlim([0, 30])# duration_H])
#    ax2.set_ylim([0, 60])# peak1_D])
    ax2.grid(which='major')
    ax2.set_ylabel('total sum [mm/event]', fontsize=8) 
    ax2.set_xlabel('event duration [consecutive wet hours (>.2mm)]', fontsize=8) 
    #ax2.set_yscale('log')      

    ''' Event duration against hourly maxima '''    
    ax3.plot(Hourframe[station].duration.values, Hourframe[station]['mean rain rate'].values,
             marker='x', linestyle='', color='red')    
#    ax3.set_xlim([0, 30])# duration_H])
#    ax3.set_ylim([0, 60])# peak1_D])
    ax3.grid(which='major')
    ax3.set_ylabel('mean rain rate [mm/h]', fontsize=8) 
    ax3.set_xlabel('event duration [consecutive wet hours (>.2mm)]', fontsize=8) 
    #ax3.set_yscale('log') 

fig.savefig(plotpath+'/'+ 'HourEvents_ZAMG10min_JJA', dpi=300)