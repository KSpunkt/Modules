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


# all observations > 1.9mm/10min (AMJJASO)
df_gr019mm = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\p_greater_019m_all.npy')
# replaces NaN with 0
# df_gr019mm_fillnan = df_gr019mm.fil

hourlysums = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\hourly_sums.npy')
dailysums = pd.read_pickle('I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Precip_grater_1point9mm\daily_sums.npy')

plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_PDFs'

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Probability density
tet = df_gr019mm.values
tet[tet==0] = np.nan
test = tet[pd.notnull(tet)]
test_sorted = np.sort(test)
percentiles_p10min = np.percentile(test, q=[95, 98, 99, 99.9])

counts,binEdges = np.histogram(test,bins=len(test), density=True)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])

fig, ax0 = plt.subplots(1,  figsize=(5, 3))
fig.suptitle("P", fontsize=10)
#ax0.set_xscale('log')
#ax0.set_yscale('log')
ax0.set_xlim([.2,100])
ax0.set_ylabel('probability density', fontsize=8)
ax0.set_xlabel('intensity [mm/10min]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)
plt.plot(bin_centres, counts,'r.', markersize=.5)
plt.savefig(plotpath + '/all10min_raw_PD.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)
# -------------------------------------------------------------------
# -------------------------------------------------------------------
tet = hourlysums.values
tet[tet==0] = np.nan
test = tet[pd.notnull(tet)]
percentiles_phourly = np.percentile(test, q=[95, 98, 99, 99.9])
counts,binEdges = np.histogram(test,bins=len(test), density=True)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])

fig, ax0 = plt.subplots(1,  figsize=(5, 3))
fig.suptitle("P)", fontsize=10)
#ax0.set_xscale('log')
#ax0.set_yscale('log')
#ax0.set_xlim([.2,100])
ax0.set_ylabel('probability density', fontsize=8)
ax0.set_xlabel('intensity [mm/h]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)
plt.plot(bin_centres, counts,'r.', markersize=.5)
plt.savefig(plotpath + '/allhourly_raw_PD.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)
# -------------------------------------------------------------------
# -------------------------------------------------------------------
tet = dailysums.values
tet[tet==0] = np.nan
test = tet[pd.notnull(tet)]
percentiles_pdaily = np.percentile(test, q=[95, 98, 99, 99.9])
counts,binEdges = np.histogram(test,bins=len(test), density=True)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])

fig, ax0 = plt.subplots(1,  figsize=(5, 3))
fig.suptitle("P", fontsize=10)
#ax0.set_xscale('log')
#ax0.set_yscale('log')
#ax0.set_xlim([.2,100])
ax0.set_ylabel('probability density', fontsize=8)
ax0.set_xlabel('intensity [mm/d]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)
plt.plot(bin_centres, counts,'r.', markersize=.5)
plt.savefig(plotpath + '/alldaily_raw_PD.png', cformat='png', dpi=300)
plt.clf()
plt.close(fig)
