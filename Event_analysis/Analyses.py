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
import Modules.Event_analysis.Event_statistics as es

path2 = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Events'
pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\Data_Analysis\Description\Plots'


''' IMPORT CLIMATE DATA
'''
#AHYD_all_stations = pd.read_pickle(src + '\AHYD_dailysums.npy')
ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min_allyear.npy')
ZAMG_daily_Tmax = pd.read_pickle(r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\DAILY\ZAMG_daily_Tmax_1992-2004.npy')


''' SET DETECTED OUTLIERS TO NO VALUE AND SAVE DATES TO FILE
'''
ZAMG_all_stations['11348']['19970701':'19970710'].loc[ZAMG_all_stations['11348']['19970701':'19970710']>0] = np.nan
ZAMG_all_stations['11265']['20060802'].loc[ZAMG_all_stations['11265']['20060802']>50] = np.nan
ZAMG_all_stations['11270']['20070319'].loc[ZAMG_all_stations['11270']['20070319']>50] = np.nan
ZAMG_all_stations['11270']['20070320'].loc[ZAMG_all_stations['11270']['20070320']>50] = np.nan
ZAMG_all_stations['11216']['20011108'].loc[ZAMG_all_stations['11216']['20011108']>00] = np.nan


''' Create Eventframe instance to analyze datasets (percent of NaN per event are
calculated independent of required valid numbers for resampling )
'''
ZAMG = es.Eventframe(ZAMG_all_stations, resolution='10min', season=[3,11])


'''Get wet day and wet hour events in station dataframe'''                  
# Dayframe = ZAMG.EventDays('ZAMG_MarNov_10mm', wet_day_threshold=1) 
Dayframe = pd.read_pickle(r'I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Data_Analysis/Events/ZAMG_MarNov_10mm_wet_day_event_statistics.npy')
Dayframe.columns.names = ['station', 'indicator']    

#Hourframe = ZAMG.EventHours(Dayframe, 'ZAMG_MarNov_Days10mm')   
Hourframe = pd.read_pickle(r'I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Data_Analysis/Events/ZAMG_MarNov_Days10mm_wet_hour_event_statistics.npy')
Hourframe.columns.names = ['station', 'indicator']

Rankframe = es.RSS(Dayframe)

'''----------------------------------------------------------------------------
#### ----------- 
## PLOT SKILL SCORES
#### -----------    
----------------------------------------------------------------------------''' 
# come up with new skill score concept
#rank_norm = 1/Rankframe
#bpdict= {}
#
#rank_norm.columns.names = ['station']  
#stacked = rank_norm.stack(['station'])
#stacked_reset = stacked.reset_index(level=1, drop=1)
#stk_con = pd.concat([stacked_reset, stacked_reset], axis=1)
#daysinyear = range(stk_con.index.dayofyear.min(), stk_con.index.dayofyear.max()+1)
#month = range(3,12)
#
#stk_con.columns = ['RSS', 'absmonth']
##stk_con.columns = ['RSS', 'absday']
###del stacked_reset['station']
##stk_con['absday'] = stk_con.index.dayofyear
#
#stk_con['absmonth'] = stacked_reset.index.month
#
#stk_con.reset_index(drop=1)
#stk_con.set_index('absmonth', inplace=1)
#
#ind = stk_con['RSS']
#for m in month:
#    bpdict.update({m: ind.loc[m].values})
#bpf = pd.DataFrame.from_dict(bpdict, orient='index').transpose()
#plotdict = bpf.boxplot(whis=[0,98], showfliers=1)


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
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
ANALYZE HOUR EVENTS 
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
'''

''' FIGURE '''
Seasons = {'spring':[3,4,5], 'summer':[6,7,8], 'autumn':[9,10,11]}
times_early = [0,12] # to be plotted on the left panel
times_late = [12,24] # to be plotted on the right panel
title = ''

fig, [[ax0, ax1], [ax2, ax3], [ax4, ax5]] = plt.subplots(3,2,  figsize=(14, 9))
fig.suptitle(title, fontsize=12)
axs=[[ax0, ax1], [ax2, ax3], [ax4, ax5]]
axs_twin=[[ax0.twinx(), ax1.twinx()], [ax2.twinx(), ax3.twinx()],
           [ax4.twinx(), ax5.twinx()]]

colors = ['#ffffff', '#add8e6', '#4169e1', '#ee82ee', '#b03060', '#ff1493']
scl = [0, 60] # y axis limits precip [mm]
scl_b = [0, 14000] # twin y axis limits (number of hour events)
xran = 16 # x axis limits duration of events [h]
yl = '' # ylabel is added via dummy axis axd

'''HOUR EVENTS BY SEASON AND TIME OF DAY'''
for season, ax, ax_tw in zip(['spring', 'summer', 'autumn'], axs, axs_twin):
    Hourframe_in_bef = Hourframe[np.logical_and(np.logical_or(Hourframe.index.month == Seasons[season][0],
                                                    Hourframe.index.month == Seasons[season][1],
                                                    Hourframe.index.month == Seasons[season][2]),
                                     np.logical_and(Hourframe.index.hour >= times_early[0],
                                     Hourframe.index.hour < times_early[1]
                                     ))]
    Hourframe_in_aft = Hourframe[np.logical_and(np.logical_or(Hourframe.index.month == Seasons[season][0],
                                                    Hourframe.index.month == Seasons[season][1],
                                                    Hourframe.index.month == Seasons[season][2]),
                                     np.logical_and(Hourframe.index.hour >= times_late[0], 
                                     Hourframe.index.hour < times_late[1]
                                     ))]   
    ''' * throw together events of all stations (flatten by station)
        * group by duration of events --> count (for histogram)
        * calculate statistical measures (p98, p99, p99.9, max) for each class
        '''
    for el, axy, axy_tw in zip([Hourframe_in_bef, Hourframe_in_aft], ax, ax_tw):  
        
        stk = el.stack('station')
        sample_by_indicator_a = stk.groupby('duration').quantile(q=.999)
        sample_by_indicator_b = stk.groupby('duration').quantile(q=.99)
        sample_by_indicator_c = stk.groupby('duration').quantile(q=.98)
        sample_by_indicator_d = stk.groupby('duration').max()

        sample_by_indicator_a[['max hourly', 'peak 1', 'mean rain rate']][0:xran].plot(
                    ax=axy, kind='line', ls='-', linewidth=1.5,
                    color=[colors[1], colors[3], colors[4]],
                    logy=1, legend=0)
        sample_by_indicator_b[['max hourly', 'peak 1', 'mean rain rate']][0:xran].plot(
                    ax=axy, kind='line', ls='--',
                    color=[colors[1], colors[3], colors[4]],
                    logy=1, legend=0)
        sample_by_indicator_c[['max hourly', 'peak 1', 'mean rain rate']][0:xran].plot(
                    ax=axy, kind='line', ls=':',
                    color=[colors[1], colors[3], colors[4]],
                    logy=1, legend=0)
                    
        sample_by_indicator_d[['max hourly', 'peak 1', 'mean rain rate']][0:xran].plot(
                    ax=axy, kind='line', ls='', linewidth=.5,
                    marker='o', markersize=5,
                    color=[colors[1], colors[3], colors[4]],
                    markeredgecolor='white',
                    logy=0, legend=0)            
        '''GET TOTAL NUMBER OF EVENTS FOR CLASSES -5, >5-10'''
        s = stk.duration[stk.duration<xran]
#        axy2 = axy.twinx()
        axy_tw.hist(s, bins=(range(1, xran+1)), 
                 color='grey', alpha=0.3, histtype='stepfilled', 
                 align='left', normed=0)
        axy_tw.set_ylim(scl_b)
        
        axy.set_title('')
#        axy.grid(which='minor')
        axy.grid(which='major', linestyle='', linewidth=.2, alpha=.8)
        axy.grid(which='minor', linestyle='-', linewidth=.2, alpha=.8)
        axy.xaxis.grid(False)
        axy_tw.grid('off')
        axy.set_ylim(scl)
        axy.set_ylabel(yl, fontsize=9) 
        axy.set_xlabel('', fontsize=8)         

ax0.set_ylabel('MAM', fontsize=14, fontweight='bold', rotation=0) 
ax2.set_ylabel('JJA', fontsize=14, fontweight='bold', rotation=0)   
ax4.set_ylabel('SON', fontsize=14, fontweight='bold', rotation=0)  

for axx in [ax0, ax2, ax4]: 
    axx.yaxis.set_label_coords(-.2,.5)
for axx in [ax2, ax3]:     
    axx.set_xticklabels([])
for axx in [ax0, ax1]:     
    axx.xaxis.tick_top()    
#for axx in [ax1, ax3, ax5]:     
#    axx.yaxis.tick_right()   
for axx in [ax1, ax3, ax5]:     
    axx.set_yticklabels([])    

for axx in [axs_twin[0][0], axs_twin[1][0], axs_twin[2][0]]: 
    axx.set_yticks([2000, 4000,6000, 8000,10000,12000,14000]) 
    axx.set_yticklabels([], color='grey')  
    
for axx in [axs_twin[0][1], axs_twin[1][1], axs_twin[2][1]]: 
    axx.set_yticks([2000, 4000,6000, 8000,10000,12000,14000])    
    axx.set_yticklabels(['','4k','', '8k','', '12k'], color='grey')     
    
    
axd = fig.add_axes([0.01, 0.1, .99, .99], frameon=0)
axd.patch.set_visible(False)
axd.yaxis.set_visible(False)
#axd.xaxis.set_visible(False)
axd.set_xticklabels([])
axd.set_xticks([])
axd.set_yticklabels([])
axd.set_yticks([])
#axd.set_ylabel('mm')
axd.set_xlabel('duration [h]')
axd.text(.082,.42,'[mm]', rotation=90)
axd.text(.93,.44,'number of events', rotation=-90, color='grey')
axd.text(.1,.9,'(a) before noon', fontsize=14)
axd.text(.52,.9,'(b) after noon', fontsize=14)

''' ---------------------------------------------------------------------------
bring in ZAMG daily Tmax
-------------------------------------------------------------------------------
'''





