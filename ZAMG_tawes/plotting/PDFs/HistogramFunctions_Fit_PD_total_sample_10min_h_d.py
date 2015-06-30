# -*- coding: utf-8 -*-
"""
Created on Wed Apr 08 15:54:19 2015

@author: Kaddabadda
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 11:57:40 2015

@author: Kaddabadda

topic:
define p99 on total sample, and not stationswise.
"""
runfile('I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes/stationfiles_v9.py', wdir='I:/DOCUMENTS/WEGC/02_PhD_research/04_Programming/Python/Modules/ZAMG_tawes')
#runfile()
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
import Modules.ZAMG_tawes.plotting.plot_99percentile_events as zamgplot
import scipy.stats as ss


# all observations > 1.9mm/10min (AMJJASO)
df_gr019mm = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\p_greater_019m_all.npy')
# replaces NaN with 0
# df_gr019mm_fillnan = df_gr019mm.fil

hourlysums = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\hourly_sums.npy')
dailysums = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\daily_sums.npy')

plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_PDFs'

# -------------------------------------------------------------------
treegreen = .1, .999, .1
pink = .9, 0, .9
light_coral = 0.9375, 0.5000, 0.5000
medium_orchid = 0.7266, 0.3320, 0.8242
# -------------------------------------------------------------------
# Probability density
tet = df_gr019mm.values
tet[tet==0] = np.nan
test = tet[pd.notnull(tet)]
test_sorted = np.sort(test)
percentiles_p10min = np.percentile(test, q=[95, 98, 99, 99.9])

# counts,binEdges = np.histogram(test,bins=len(test), density=True)
# counts,binEdges = np.histogram(test,bins=100, density=True)
counts,binEdges = np.histogram(test,bins=100, density=False)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])
width = 0.7 * (binEdges[1] - binEdges[0])

fig, ax0 = plt.subplots(1,  figsize=(5, 3))
fig.suptitle("10min precipitation", fontsize=10)
#ax0.set_xscale('log')
ax0.set_yscale('log')
#ax0.set_xlim([.2,50])
# ax0.set_ylabel('probability density', fontsize=8)
ax0.set_xlabel('intensity [mm/10min]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)

plt.bar(bin_centres, counts, align='center', width=width, edgecolor='None',
        color=treegreen)
plt.annotate('n: ' + str(len(test)), (.7,.75), xycoords='figure fraction')

plt.axvline(x=percentiles_p10min[3], color=pink)
plt.annotate('p99.9: ' + str(np.round(percentiles_p10min[3],2)) + 'mm', (.259,.75),
             xycoords='figure fraction', color=pink, size=8, rotation=90)

plt.plot()
plt.savefig(plotpath + '/all10min_raw_PD_hist.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)
# -------------------------------------------------------------------
# -------------------------------------------------------------------
tet = hourlysums.values
tet[tet==0] = np.nan
test = tet[pd.notnull(tet)]
percentiles_phourly = np.percentile(test, q=[95, 98, 99, 99.9])
#counts,binEdges = np.histogram(test,bins=len(test), density=True)
# counts,binEdges = np.histogram(test,bins=100, density=True)
counts,binEdges = np.histogram(test,bins=100, density=False)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])
width = 0.7 * (binEdges[1] - binEdges[0])
fig, ax0 = plt.subplots(1,  figsize=(5, 3))
fig.suptitle("hourly precipitation", fontsize=10)
#ax0.set_xscale('log')
ax0.set_yscale('log')
#ax0.set_xlim([.2,100])
# ax0.set_ylabel('probability density', fontsize=8)
ax0.set_xlabel('intensity [mm/h]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)
plt.bar(bin_centres, counts, align='center', width=width, edgecolor='None', color=treegreen)
plt.annotate('n: ' + str(len(test)), (.7,.75), xycoords='figure fraction')

plt.axvline(x=percentiles_phourly[3], color=pink)
plt.annotate('p99.9: ' + str(np.round(percentiles_phourly[3],2)) + 'mm', (.31,.75),
             xycoords='figure fraction', color=pink, size=8, rotation=90)

plt.savefig(plotpath + '/allhourly_raw_PD_hist.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)
# -------------------------------------------------------------------
# -------------------------------------------------------------------
tet = dailysums.values
tet[tet==0] = np.nan
test = tet[pd.notnull(tet)]
percentiles_pdaily = np.percentile(test, q=[95, 98, 99, 99.9])
# counts,binEdges = np.histogram(test,bins=len(test), density=True)
# counts,binEdges = np.histogram(test,bins=100, density=True)
counts,binEdges = np.histogram(test,bins=100, density=False)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])
width = 0.7 * (binEdges[1] - binEdges[0])
fig, ax0 = plt.subplots(1,  figsize=(5, 3))
fig.suptitle("daily precipitation", fontsize=10)
#ax0.set_xscale('log')
ax0.set_yscale('log')
#ax0.set_xlim([.2,100])
# ax0.set_ylabel('probability density', fontsize=8)
ax0.set_xlabel('intensity [mm/d]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)
plt.bar(bin_centres, counts, align='center', width=width, edgecolor='None',
        color=treegreen)
plt.annotate('n: ' + str(len(test)), (.7,.75), xycoords='figure fraction')

plt.axvline(x=percentiles_pdaily[3], color=pink)
plt.annotate('p99.9: ' + str(np.round(percentiles_pdaily[3],2)) + 'mm', (.4,.75),
             xycoords='figure fraction', color=pink, size=8, rotation=90)

plt.savefig(plotpath + '/alldaily_raw_PD_hist.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)


### --------------------------------------------------------
# plot date all stations in 10min resolution and max station in pink
### --------------------------------------------------------
fig, ax0 = plt.subplots(1,  figsize=(8, 3))
fig.suptitle("Precipitation 04.09.2009, 10min resolution, ZAMG stations", fontsize=10)
df_gr019mm['09/04/2009'].plot(colormap='winter', legend=False, ax=ax0)
#df_gr019mm['09/04/2009'].plot(color=treegreen, legend=False, ax=ax0)
df_gr019mm['11217']['09/04/2009'].plot(color=medium_orchid, ax=ax0)
plt.axhline(y=8.3, color='r')
plt.annotate('DWD very heavy', (.1,.55), xycoords='figure fraction', color='r', fontsize=7)

plt.axhline(y=1.7, color='r')
plt.annotate('DWD heavy', (.1,.25), xycoords='figure fraction', color='r', fontsize=7)

ax0.set_ylabel('[mm]', fontsize=8)
# ax0.set_xlabel('intensity [mm/d]', fontsize=8)
plt.savefig(plotpath + '/20090904_10min.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)