# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:04:11 2015

@author: Kaddabadda
"""
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
from itertools import izip

path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description\Plots'

''' IMPORT RAW DATA
'''
#AHYD_all_stations = pd.read_pickle(src + '\AHYD_dailysums.npy')
ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min_allyear.npy')

''' SET DETECTED OUTLIERS TO NO VALUE AND SAVE DATES TO FILE
'''
ZAMG_all_stations['11348']['19970701':'19970710'].loc[ZAMG_all_stations['11348']['19970701':'19970710']>0] = np.nan
ZAMG_all_stations['11265']['20060802'].loc[ZAMG_all_stations['11265']['20060802']>50] = np.nan
ZAMG_all_stations['11270']['20070319'].loc[ZAMG_all_stations['11270']['20070319']>50] = np.nan
ZAMG_all_stations['11270']['20070320'].loc[ZAMG_all_stations['11270']['20070320']>50] = np.nan
ZAMG_all_stations['11216']['20011108'].loc[ZAMG_all_stations['11216']['20011108']>00] = np.nan

import Modules.Event_analysis.Event_statistics as es
'''
Create Eventframe instance to analyze datasets (percent of NaN per event are
calculated independent of required valid numbers for resampling )
'''
ZAMG_reduced = pd.concat([ZAMG_all_stations['11173']['2012'], ZAMG_all_stations['11148']['2012']], axis=1)

ZAMG = es.Eventframe(ZAMG_all_stations, resolution='10min', season=[3,11])

'''Get wet day and wet hour events in station dataframe'''                  
Dayframe = ZAMG.EventDays('ZAMG_MarNov_10mm', wet_day_threshold=1) 
Dayframe.columns.names = ['station', 'indicator']    
Hourframe = ZAMG.EventHours(Dayframe, 'ZAMG_MarNov_Days10mm')   

Rankframe = es.RSS(Dayframe)

'''----------------------------------------------------------------------------
#### ----------- 
## PLOT SKILL SCORES
#### -----------    
----------------------------------------------------------------------------''' 
rank_norm = 1/Rankframe
bpdict= {}

rank_norm.columns.names = ['station']  
stacked = rank_norm.stack(['station'])
stacked_reset = stacked.reset_index(level=1, drop=1)
stk_con = pd.concat([stacked_reset, stacked_reset], axis=1)
daysinyear = range(stk_con.index.dayofyear.min(), stk_con.index.dayofyear.max()+1)
month = range(3,12)

stk_con.columns = ['RSS', 'absmonth']
#stk_con.columns = ['RSS', 'absday']
##del stacked_reset['station']
#stk_con['absday'] = stk_con.index.dayofyear

stk_con['absmonth'] = stacked_reset.index.month

stk_con.reset_index(drop=1)
stk_con.set_index('absmonth', inplace=1)

ind = stk_con['RSS']
for m in month:
    bpdict.update({m: ind.loc[m].values})
bpf = pd.DataFrame.from_dict(bpdict, orient='index').transpose()
plotdict = bpf.boxplot(whis=[0,98], showfliers=1)

'''----------------------------------------------------------------------------
#### ----------- 
## PLOT DAY EVENTS
#### -----------    
----------------------------------------------------------------------------'''    
fig, [[ax, ax1], [ax2, ax3]] = plt.subplots(2,2,  figsize=(9, 9))
fig.suptitle("Day Events ZAMG 10min", fontsize=12)

axs = [ax, ax1, ax2, ax3]
cols = ['peak 1', 'max daily', 'max h 1', 'sum']
ylabels = ['mm/10min', 'mm/d', 'mm/d', 'total mm']
colors = ['#ff1493', '#b03060', '#4169e1', '#add8e6']

for station in Dayframe.columns.get_level_values(0).drop_duplicates():
    for a, c, cl in zip(axs, cols, colors):
        ''' Event duration against high resolution peaks '''
        a.plot(Dayframe[station].duration.values, Dayframe[station][c].values,
                 marker='.', linestyle='', color=cl)
        
'''AXES PROPERTIES
'''
for a, l, c in zip(axs, ylabels, cols):
    a.set_title(c)
    a.grid(which='minor')
    a.set_ylabel(l, fontsize=8) 
    a.set_xlabel('event duration [consecutive wet days (>2mm)]', fontsize=8) 
    #a.set_yscale('log')    
    
fig.savefig(plotpath+'/'+ 'DayEvents_ZAMG_MarNov10mm', dpi=300)
                
'''----------------------------------------------------------------------------
#### ----------- 
## PLOT HOUR EVENTS
#### -----------    
----------------------------------------------------------------------------'''    
            
mpl.style.use('bmh')            
fig, [[ax, ax1], [ax2, ax3]] = plt.subplots(2,2,  figsize=(9, 9))
fig.suptitle("Hour Events ZAMG 10min", fontsize=12)

axs = [ax, ax1, ax2, ax3]
cols = ['peak 1', 'max hourly', 'sum', 'mean rain rate']
ylabels = ['mm/10min', 'mm/h', 'mm total', 'mm/h']
colors = ['#ff1493', '#b03060', '#4169e1', '#add8e6']#, '#4169e1', '#ee82ee', '#b03060', '#ff1493']
    
    
for [i, station] in enumerate(Hourframe.columns.get_level_values(0).drop_duplicates()):
    for a, c, cl in zip(axs, cols, colors):
        a.plot(Hourframe[station].duration.values, Hourframe[station][c].values,
             marker='.', linestyle='', color=cl)             

'''AXES PROPERTIES
'''
for a, l, c in zip(axs, ylabels, cols):
    a.set_title(c)
    a.grid(which='minor')
    a.set_ylabel(l, fontsize=8) 
    a.set_xlabel('event duration [consecutive wet hours ]', fontsize=8) 
    ##a.set_yscale('log') 

fig.savefig(plotpath+'/'+ 'HourEvents_ZAMG_MarNov10mm', dpi=300)


'''----------------------------------------------------------------------------
#### ----------- 
## PLOT SKILL SCORE
#### -----------    
----------------------------------------------------------------------------'''    
 
        
ax = (Rankframe).plot(marker='.', markersize=5,linestyle='', legend=0,
                        title='DAY EVENTS', colormap='Set3')# , logy=1)        
ax.set_ylabel('RSS')   
#ax.set_ylim([0,1.2])
ax.set_xlabel('') 

'''----------------------------------------------------------------------------
#### ----------- 
## PLOT BOXPLOTS
#### -----------    
----------------------------------------------------------------------------'''    
def Event_boxplot(Frame, kind='Day', filename_extension='',
                  title_extension=''):
    if kind == 'Day':
        ''' indicators DAY events'''
        indicator =  ['sum', 'max daily', 'max h 1', 'peak 1'] #, 'max h 2']
        labels = ['mm total', 'mm/d', 'mm/h', 'mm/10min'] #, 'mm/h']
        title = 'Day events'
    elif kind == 'Hour':
        ''' indicators HOUR events'''
        indicator =  ['sum', 'max hourly', 'peak 1', 'duration']
        labels = ['mm total', 'mm/h', 'mm/10min', 'h']
        title = 'Hour events'
        
    mpl.style.use('bmh')
#    pd.options.display.mpl_style = False
        
        
    bpdict = {}
    month = range(3,12)
 
    Frame.columns.names = ['station', 'indicator']  
    stacked = Frame.stack(['station'])
    stacked_reset = stacked.reset_index(level=1, drop=1)
    #del stacked_reset['station']
    stacked_reset['absmonth'] = stacked_reset.index.month
    
    stacked_reset.reset_index(drop=1)
    stacked_reset.set_index('absmonth', inplace=1)
    
    #fig, [[ax, ax1], [ax2, ax3], [ax4, ax5]] = plt.subplots(3,2,  figsize=(13, 10))
    fig, [[ax, ax1], [ax2, ax3]] = plt.subplots(2,2,  figsize=(9, 9))
    
    fig.suptitle(title +', '+ title_extension, fontsize=12)
    
    axs=[ax, ax1, ax2, ax3]
    colors = ['#ffffff', '#add8e6', '#4169e1', '#ee82ee', '#b03060', '#ff1493']
    
    for i, axz in zip(indicator, axs):
        ind = stacked_reset[i]
        for m in month:
            bpdict.update({m: ind.loc[m].values})
        bpf = pd.DataFrame.from_dict(bpdict, orient='index').transpose()
        plotdict = bpf.boxplot(ax=axz, whis=[0, 99.9], showfliers=1)
        plt.setp(plotdict['fliers'], color=colors[5], marker='x')
        plt.setp(plotdict['whiskers'], color=colors[2])
        plt.setp(plotdict['medians'], color=colors[1], linewidth=2.5)
        plt.setp(plotdict['caps'], color=colors[4], linewidth=2.5)
    
    '''AXES PROPERTIES
    '''
    scale = [[0,300],[0,100],[0,50],[0,100]]
    for a, i, l, scl in zip(axs, indicator, labels, scale):
        a.set_title(i)
        a.grid(which='minor')
        a.set_ylim(scl)
        a.set_ylabel(l, fontsize=9) 
        a.set_xlabel('', fontsize=8) 
        a.set_xticklabels(['M', 'A', 'M', 'J', 'J', 'A','S', 'O', 'N'])  
        #a.set_yscale('log')  
    
    plt.annotate('all boxplots:', (.09,.88), color='black',
                xycoords='figure fraction')     
    plt.annotate('whis [0, 99.9]', (.09,.84), color=colors[2],
                xycoords='figure fraction')    
    ax2.annotate('median', (.09,.86), color=colors[1],
                xycoords='figure fraction')
    ax3.annotate('fliers > p99.9', (.09,.82), color=colors[5],
                xycoords='figure fraction')
       
    fig.show()
    fig.savefig(plotpath+'/'+ kind + '_Events_ZAMG_MarNov10mm_bp_leg_' +
                 filename_extension, dpi=300)


'''----------------------------------------------------------------------------
ANALYZE HOUR EVENTS 
-------------------------------------------------------------------------------
'''
# load hour events data frame 'hedf'

hedf = pd.read_pickle(r'I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Data_Analysis/Events/ZAMG_MarNov_Days10mm_wet_hour_event_statistics.npy')
hedf.columns.names = ['station', 'indicator']


'''CHOOSE HOUR EVENTS BY TIME'''
hedf_in = hedf[np.logical_and(hedf.index.hour > 15,
                              np.logical_or(hedf.index.month == 3,
                                            hedf.index.month == 4,
                                            hedf.index.month == 5)
                              )]


'''# accsess dataframe?
hedf.iloc[:, hedf.columns.get_level_values(1)=='duration']
# drops 'duration'
df_dur = hedf.xs('duration', level=1, axis=1) == 3
dur_3 = hedf[hedf.xs('duration', level='indicator', axis=1, drop_level=0)==3]
'''
      
''' ---------------------------------------------------------------------------
STACK THE DATAFRAME ON STATIONS (station as index, not column)'''
stk = hedf_in.stack('station') 

''' ---------------------------------------------------------------------------
ANY ADJUSTMENTS OR STATS CALCULATIONS BY INDICATOR (e.g., duration) 
AND MEASURE (e.g., mean(), max(), quantile(q=.5))
''' 
#dur_short = stk[stk.duration<5]  
#dur_long =  stk[stk.duration>5]  

''' date and station of the max values'''
#idx_by_indicator = stk.groupby('duration').idxmax().head()

'''calculate statistical measure of the sample'''
#sample_by_indicator = stk.groupby('duration').mean()
#sample_by_indicator = stk.groupby('duration').max()
sample_by_indicator = stk.groupby('duration').quantile(q=.99)

''' ---------------------------------------------------------------------------
FIGURE

plot duration on the x axis, hourly and 10 min peaks in spring autumn summer

plot duration on the x axis and onset time after noon or pre noon for the seasons

* highest peaks in record in summer, short time, and afternoon onset
'''
title = ''

fig, [[ax, ax1], [ax2, ax3]] = plt.subplots(2,2,  figsize=(9, 9))

fig.suptitle(title, fontsize=12)

axs=[ax, ax1, ax2, ax3]
colors = ['#ffffff', '#add8e6', '#4169e1', '#ee82ee', '#b03060', '#ff1493']
 

sample_by_indicator[['peak 1', 'max hourly']][0:24].plot(ax=ax1, kind='bar',
                  color=[colors[2], colors[3]], logy=0, legend=0)





# get p 95 by duration



