# -*- coding: utf-8 -*-
"""
Created on Thu Mar 05 11:45:31 2015

@author: Kaddabadda

Visualize PDFs of 10 min data (all, raw, uncorrected)
- delete Station errors (Mariapfarr, ?)
"""

runfile('I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes/stationfiles_v9.py', wdir='I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes')

import matplotlib as mpl

import numpy as np
import pandas as pd
import csv
import os
import numpy.ma as ma
import xray as xr
import matplotlib.pyplot as plt
import stationfiles_v9 as zamg
import matplotlib.dates as dates
import Modules.ZAMG_tawes.plotting.plot_99percentile_events as plot99

# load dataframe with all p>0.19mm/10min

df_gr019mm = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\p_greater_019m_all.npy')

# load dataframe containing Temperature
df_pth = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\ZAMG\processed_data\Station_Dataframes'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_PDFs\P_other_Variables'

# identify possible station errors
outlier_folder = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\99th_percentile\Outlier_analysis'
days = ['1996-07-02', '1995-09-04', '2011-08-03', '2011-09-01', '2008-06-24',
        '1996-06-10', '2009-08-22', '2013-08-29', '2006-08-02', '2000-06-21',
        '2001-07-29', '1998-06-10', '1997-07-03', '2003-06-24', '2004-08-06',
        '2007-09-03']
statnrs = [11220, 11220, 11238, 11244, 11244, 11248, 11249, 11249, 11265,
           11265, 11265, 11292, 11348, 11349, 11390, 11218]
for eachDay, eachNr in zip(days, statnrs):
    print eachDay, eachNr
    plot99.plot_Station_Daily_total(df_gr019mm[eachDay], eachNr, outlier_folder, eachDay)

def concat_all_df(above):
    ''' read all Station dataframes and concat, pass above for a threshold in
    mm/10min
    '''
    i=-1
    for eachStation in zamg.statlist:
        i = i+1
        df_test = pd.read_csv(df_pth + '\DataFrame_' + str(eachStation) + '.csv',
                              index_col=0, usecols=[0,'temperature','precip',
                              'rel_hum', 'pressure'])

        df_test2 = df_test[df_test['precip']>0.19]
        # delete 3.7.1996 for Mariapfarr 11348 and
        # 2.8.2006 for 11265 (records 99.9mm in 10min)
        if eachStation == 11348:
            del df_test2['1997-07-03']
        if eachStation == 11265:
            del df_test2['2006-08-02']

        if i==0:
            df_all = df_test2
        else:
            df_all = df_all.append(df_test2, ignore_index=True)
        print 'loop_', i

    df_all = df_all[df_all['precip'] > above]
    return df_all

def plot_PDF_all_raw(df_all, plotpath):
    ''' input dataframe needs columns precip, temperature, rel_hum and pressure
    subplots for T, rF, dpT
    '''
    fig, [(ax0, ax1), (ax2, ax3)] = plt.subplots(2,2,  figsize=(10, 10), sharey=True)
    fig.suptitle("ZAMG SE Alpine", fontsize=14)
    ax0.hexbin(df_all['temperature'], df_all['precip'], yscale='log',
                      gridsize=50, bins='log') #bins='log'
    ax0.set_title(str(df_all.columns[2]) + '_vs_' + str(df_all.columns[0]))
    ax0.set_ylim([8.3,100])
    ax0.set_xlim([10,25])
    ax0.annotate('T [deg C]', xy = (.5, -.1), xycoords='axes fraction',
                     va='center', fontsize=10, color='k')

    ax1.hexbin(df_all['rel_hum'], df_all['precip'], yscale='log',
                      gridsize=50, bins='log')
    ax1.set_xlim([0,100])
    ax1.set_title(str(df_all.columns[2]) + '_vs_' + str(df_all.columns[1]))
    ax1.annotate('rel hum [percent]', xy = (.5, -.1), xycoords='axes fraction',
                     va='center', fontsize=10, color='k')

    ax2.hexbin(df_all['pressure'], df_all['precip'], yscale='log',
                      gridsize=50, bins='log')
    ax2.set_xlim([450,1100])
    ax2.set_title(str(df_all.columns[2]) + '_vs_' + str(df_all.columns[3]))
    ax2.annotate('p [hPa]', xy = (.5, -.2), xycoords='axes fraction',
                     va='center', fontsize=10, color='k')

    ax0.annotate('[mm/10min]', xy = (-.2, .0), xycoords='axes fraction',
                     va='center', fontsize=10, color='k', rotation=90)

    plt.savefig(plotpath + str(df_all.columns[2]) + 'gr8-3mm_10-25deg_vs_vars.png',
                format='png', dpi=300)
    plt.clf()
    plt.close(fig)

    #mpl.pyplot.hexbin(df_test2['temperature'], df_test2['precip'],
    #                  gridsize=50, bins='log')
