# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 11:41:43 2015

@author: Kaddabadda
"""
# FIGURE 99th percentile events, each station
# ------------------------------

import matplotlib as mpl

import numpy as np
import pandas as pd
import csv
import os
import numpy.ma as ma
#import xray as xr
import matplotlib.pyplot as plt
import Modules.ZAMG_tawes.stationfiles_v9 as zamg
import matplotlib.dates as dates
from Modules.ZAMG_tawes.plotting.colors import *

plotpath = r'I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/plots/time_series_plots/'

def boxplot_percentiles(dataframe, filename):
    ''' plots a boxplots of percentiles (whistkers at 2, 99th perc) of all
    station records in the input dataframe,
    --> saves to Python/plots
	--> filename: str(filename for png)
    '''
    fig, ax0 = plt.subplots(1,  figsize=(15, 5))
    ax0.set_yscale('log')
    # set label properties
    fig.text(0.1, 0.5, 'input precip data [mm]', va='center', rotation='vertical',
             fontsize=11)
    fig.text(0.5, 0.001, 'percentile', va='center', fontsize=11)
    # set plot styles
    markerStyle = 'bx'
    wid = 0.5
    perc = [1, 99]
    dataframe.boxplot(ax=ax0, whis=perc)
    plt.setp(ax0.get_xticklabels(), rotation=85)
    # plt.savefig(plotpath + 'boxplot_allstats_percentiles.eps', format='eps', dpi=300)
    plt.savefig(plotpath + 'boxplot_' + filename + '.png', format='png', dpi=300)
    plt.clf()
    plt.close(fig)

def plot_Station_Zoom(dataframe, statnr, start, end):
    '''plots station record of given dataframe (saves to Pythons/plots)
    start, end: string of 'YYYY/MM/DD HH:MM'
    '''
    name = zamg.stat_dict.keys()[zamg.stat_dict.values().index(str(statnr))]
    df = dataframe[str(statnr)]
    df = df.dropna()
    idx = df.index
    fig, [ax0, ax1] = plt.subplots(2,  figsize=(9, 7))
    ax0.set_yscale('log')
    ax0.plot(idx.to_pydatetime(), df, c=graublau, marker='.', linestyle=' ')
    ax0.xaxis_date()
        # plot physical extreme definitions
    ax0.plot(idx, np.transpose(np.ones((len(df)))*1.7), c=graurot, ls='--')
    ax0.text(idx[0], 1.7, 'DWD heavy', size=7, color=graurot)
    ax0.plot(idx, np.transpose(np.ones((len(df)))*8.3), c=graurot, ls='-.')
    ax0.text(idx[0], 8.3, 'DWD very heavy', size=7, color=graurot)
    ax0.set_title(str(name) + '(' + str(statnr) + '), total summer rec and zoom')
    # set label properties
    ax0.text(0.01, 0.5, '[mm/10min]', va='center', rotation='vertical',
             fontsize=11)
    ax0.xaxis.grid(True, which="minor")
    ax0.yaxis.grid()
#    ax0.text(0.6, 0.8, str(name), va='center', fontsize=18)
#    ax0.text(0.6, 0.75, 'AMJJAS, >0.19mm', va='center', fontsize=9)

    df1 = df[start:end]
    idx1 = df1.index
    ax1.bar(idx1.to_pydatetime(), df1, width=0.001, color='.7', edgecolor=graublau)
    ax1.xaxis_date()
    # plot physical extreme definitions
    ax1.plot(idx1, np.transpose(np.ones((len(df1)))*1.7), c=graurot, ls='--')
    ax1.text(idx1[1], 1.7, 'DWD heavy', size=7, color=graurot)
    ax1.plot(idx1, np.transpose(np.ones((len(df1)))*8.3), c=graurot, ls='-.')
    ax1.text(idx1[1], 8.3, 'DWD very heavy', size=7, color=graurot)
    ax1.xaxis.set_minor_locator(dates.HourLocator())
    ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))
    plt.setp(ax1.xaxis.get_minorticklabels(), rotation=90)
    ax1.xaxis.grid(True, which="minor")
    ax1.yaxis.grid()
    ax1.xaxis.set_major_locator(dates.YearLocator())
    ax1.xaxis.set_major_formatter(dates.DateFormatter('\n %B %Y'))
    #plt.savefig(plotpath + str(name) + '_zoom.eps', format='eps', dpi=300)
    plt.savefig(plotpath + str(name) + '_zoom.png', format='png', dpi=300)
    plt.clf()
    plt.close(fig)

def plot_Station_Daily_total(dataframe, statnr, directory, filename_ext):
    '''plots station record of given dataframe (saves to Pythons/plots)
    start, end: string of 'YYYY/MM/DD HH:MM'
    '''
    name = zamg.stat_dict.keys()[zamg.stat_dict.values().index(str(statnr))]
    df = dataframe[str(statnr)]
    df[np.isnan(df)] = 0
    idx = df.index
    fig, ax1 = plt.subplots(1,  figsize=(5, 2))

    #    df1 = df[start:end]
    #    idx1 = df1.index
    ax1.bar(idx.to_pydatetime(), df, width=0.001, color='.7', edgecolor=graublau)
    ax1.xaxis_date()
    ax1.set_ylim([0,50])
    # plot physical extreme definitions
    ax1.plot(idx, np.transpose(np.ones((len(df)))*1.7), c=graurot, ls='--')
    ax1.text(idx[1], 1.7, 'DWD heavy', size=7, color=graurot)
    ax1.plot(idx, np.transpose(np.ones((len(df)))*8.3), c=graurot, ls='-.')
    ax1.text(idx[1], 8.3, 'DWD very heavy', size=7, color=graurot)
    ax1.xaxis.set_minor_locator(dates.HourLocator())
    # ax1.xaxis.set_minor_locator(dates.MinuteLocator(interval=60))

    ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:00'))
    plt.setp(ax1.xaxis.get_minorticklabels(), rotation=90, fontsize=5)
    plt.setp(ax1.get_yticklabels(), fontsize=5)
    ax1.xaxis.grid(True, which="minor")
    ax1.yaxis.grid()
    ax1.xaxis.set_major_locator(dates.YearLocator())
    ax1.xaxis.set_major_formatter(dates.DateFormatter('\n %B %Y'))
    ax1.annotate('[mm]', xy = (-.06, .5), xycoords='axes fraction',
                 va='center', fontsize=5, color='k', rotation=90)
    #plt.savefig(plotpath + str(name) + '_zoom.eps', format='eps', dpi=300)
    plt.savefig(directory + '/' + str(statnr) + '_' + str(filename_ext) + '.png', format='png', dpi=300)
    plt.clf()
    plt.close(fig)


def plot_99events(statnr, df10min, dfhourly, dfdaily):  # add kind of events (daily, hourly, etc)
    ''' plots all records > 99th percentile for 10min, hourly and daily sums
    of given input dataframes in three subplots
    '''
    name = zamg.stat_dict.keys()[zamg.stat_dict.values().index(str(statnr))]
    s = df10min
    s1 = dfhourly
    s2 = dfdaily

    idx = s.index
    idx1 = s1.index
    idx2 = s2.index

    fig, [ax0, ax1, ax2] = plt.subplots(3, figsize=(13, 6.5), sharex=True)

    # ----------------------------
    # plot 10 min 99th percentile
    # ----------------------------
    ax0.bar(idx.to_pydatetime(), s, width=.5, color='b', edgecolor='b')
    ax0.xaxis_date()
    ax0.set_ylim([0,30])
    # plot physical extreme definitions
    ax0.plot(idx, np.transpose(np.ones((len(s)))*1.7), c=graurot, ls='--')
    ax0.text(idx[1], 1.7, 'DWD heavy', size=7, color=graurot)
    ax0.plot(idx, np.transpose(np.ones((len(s)))*8.3), c=graurot, ls='-.')
    ax0.text(idx[1], 8.3, 'DWD very heavy', size=7, color=graurot)
    ax0.plot(idx, np.transpose(np.ones((len(s)))*17), c=graurot, ls=':')
    ax0.text(idx[1], 17, 'Schmid&Wuest extreme', size=7, color=graurot)

    ax0.xaxis.set_minor_locator(dates.MonthLocator(bymonth=(4, 11),
                                interval=1))
    ax0.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    ax0.xaxis.grid(True, which="minor")
    ax0.yaxis.grid()
        # ----- label extremes -----------------------
    s_xtr = s[s > s.quantile(q=.95)]
    for i in range(0, len(s_xtr), 2):
        ax0.annotate(s_xtr.index.to_pydatetime()[i].strftime('%d.%m. %H:%M'),
                     xy=(dates.date2num(s_xtr.index[i]), s_xtr[i]),
                     rotation=0, size='small', va='top', ha='left',
                     xytext=(-60, -20), textcoords='offset points',
                     arrowprops=dict(arrowstyle='-|>'), bbox=(dict(facecolor=
                     'white', edgecolor='white', alpha=0.5)), color='.5')
    for i in range(1, len(s_xtr), 2):
        ax0.annotate(s_xtr.index.to_pydatetime()[i].strftime('%d.%m. %H:%M'),
                     xy=(dates.date2num(s_xtr.index[i]), s_xtr[i]),
                     rotation=0, size='small', va='top', ha='right',
                     xytext=(60, -15), textcoords='offset points',
                     arrowprops=dict(arrowstyle='-|>'), bbox=(dict(facecolor=
                     'white', edgecolor='white', alpha=0.5)), color='.5')
    ax0.xaxis.set_major_locator(dates.YearLocator())
    ax0.xaxis.set_major_formatter(dates.DateFormatter('\n\n%Y'))
    ax0.annotate('n: ' + str(len(s)), xy = (.01, .9),
                 xycoords='axes fraction', va='center', fontsize=14,
                 color='b', bbox=(dict(facecolor='blue', alpha=0.2)))
    ax0.annotate('[mm/10min]', xy = (-.05, .5), xycoords='axes fraction',
                 va='center', fontsize=10, color='k', rotation=90)
    # ----------------------------
    # plot hourly 99th percentile
    # ----------------------------
    ax1.bar(idx1.to_pydatetime(), s1, width=.5, color='k', edgecolor='k')
    ax1.set_ylim([0,60])
    ax1.xaxis_date()
    ax1.xaxis.grid(True, which="minor")
    ax1.yaxis.grid()
    # plot physical extreme definitions
    ax1.plot(idx1, np.transpose(np.ones((len(s1)))*10), c=graurot, ls='--')
    ax1.text(idx[1], 10, 'DWD heavy', size=7, color=graurot)
    ax1.plot(idx1, np.transpose(np.ones((len(s1)))*50), c=graurot, ls='-.')
    ax1.text(idx[1], 50, 'DWD very heavy', size=7, color=graurot)

    # ----- label extremes -----------------------
    s1_xtr = s1[s1 > s1.quantile(q=.95)]
    for i in range(0, len(s1_xtr), 2):
        ax1.annotate(s1_xtr.index.to_pydatetime()[i].strftime('%d.%m. %H h'),
                     xy=(dates.date2num(s1_xtr.index[i]), s1_xtr[i]),
                     rotation=0, size='small', va='top', ha='left',
                     xytext=(-50, -20), textcoords='offset points',
                     arrowprops=dict(arrowstyle='-|>'), bbox=(dict(facecolor=
                     'white', edgecolor='white', alpha=0.5)), color='.5')
    for i in range(1, len(s1_xtr), 2):
        ax1.annotate(s1_xtr.index.to_pydatetime()[i].strftime('%d.%m. %H h'),
                     xy=(dates.date2num(s1_xtr.index[i]), s1_xtr[i]),
                     rotation=0, size='small', va='top', ha='right',
                     xytext=(50, -20), textcoords='offset points',
                     arrowprops=dict(arrowstyle='-|>'), bbox=(dict(facecolor=
                     'white', edgecolor='white', alpha=0.5)), color='.5')
    # ----- labels and number of observations
    ax1.annotate('n: ' + str(len(s1)), xy = (.01, .9),
             xycoords='axes fraction', va='center', fontsize=14,
             color='k', bbox=(dict(facecolor='black', alpha=0.2)))
    ax1.annotate('[mm/h]', xy = (-.05, .5), xycoords='axes fraction',
                 va='center', fontsize=10, color='k', rotation=90)
    # ----------------------------
    # plot daily 99th percentile
    # ----------------------------
    ax2.bar(idx2.to_pydatetime(), s2, width=.3, color='r', edgecolor='r')
    ax2.set_ylim([0,190])
    ax2.xaxis_date()
    ax2.xaxis.grid(True, which="minor")
    ax2.yaxis.grid()
    # ----- label extremes -----------------------
    for i in range(0, len(s2), 3):
        ax2.annotate(idx2.to_pydatetime()[i].strftime('%d.%m'),
                         xy=(dates.date2num(s2.index[i]), s2[i]),
                         rotation=0, size='small', va='top', ha='left',
                         xytext=(20, 20), textcoords='offset points',
                         arrowprops=dict(arrowstyle='-|>'), bbox= (dict(
                         facecolor='white', edgecolor='white', alpha=0.5)),
                         color='.5')

    for i in range(1, len(s2), 3):
        ax2.annotate(idx2.to_pydatetime()[i].strftime('%d.%m'),
                         xy=(dates.date2num(s2.index[i]), s2[i]),
                         rotation=0, size='small', va='bottom', ha='right',
                         xytext=(-20, 5), textcoords='offset points',
                         arrowprops=dict(arrowstyle='-|>'), bbox=(dict(
                         facecolor='white', edgecolor='white', alpha=0.5)),
                         color='.5')

    for i in range(2, len(s2), 3):
        ax2.annotate(idx2.to_pydatetime()[i].strftime('%d.%m'),
                         xy=(dates.date2num(s2.index[i]), s2[i]),
                         rotation=0, size='small', va='bottom', ha='left',
                         xytext=(-40, -40), textcoords='offset points',
                         arrowprops=dict(arrowstyle='-|>'), bbox=(dict(
                         facecolor='white', edgecolor='white', alpha=0.5)),
                         color='.5')

    ax2.annotate('n: ' + str(len(s2)), xy = (.01, .9),
             xycoords='axes fraction', va='center', fontsize=14,
             color='r', bbox=(dict(facecolor='red', alpha=0.2)))
    ax2.annotate('[mm/d]', xy = (-.05, .5), xycoords='axes fraction',
                 va='center', fontsize=10, color='k', rotation=90)

    ax0.set_title('Events > 99th percentile (Apr-Nov), ' + name)
    plt.setp(ax0.get_xticklabels(), rotation=0)
    plt.tight_layout()

    # fig.savefig('test.png', format='png', dpi=300)
    # fig.savefig(plotpath + str(statnr) + 'Events99.eps', format='eps', dpi=300)
    plt.savefig(plotpath + str(statnr) + 'Events99.png', format='png', dpi=300)
    plt.clf()
    plt.close(fig)
