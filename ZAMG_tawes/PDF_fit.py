# -*- coding: utf-8 -*-
"""
Created on Sun Jun 07 16:33:45 2015

@author: Kaddabadda
"""
import numpy as np
import matplotlib.pyplot as plt
#import scipy as sp
import scipy.stats as ss
import Modules.ZAMG_tawes.Sample_definition as eventdates

pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'
plotpath = r'I:\DOCUMENTS\WEGC\02_PhD_research\04_Programming\Python\plots\precip_PDFs'

ZAMG_all_stations = pd.read_pickle(pth2 + '\ZAMG_10min.npy')
AHYD_all_stations = pd.read_pickle(src + '\AHYD_allstations_summer.npy')
# Mariapfarr and 11265 crazy Rain
ZAMG_all_stations['11348']['19970703'].loc[ZAMG_all_stations['11348']['19970703']>30] = np.nan
ZAMG_all_stations['11348']['19970704'].loc[ZAMG_all_stations['11348']['19970704']>30] = np.nan
ZAMG_all_stations['11265']['20060802'].loc[ZAMG_all_stations['11265']['20060802']>50] = np.nan

# remove all zeros and NAN
ZAMG_all_stations[ZAMG_all_stations==0] = np.nan
ZAMG_all_stations[ZAMG_all_stations==0.1] = np.nan
data = ZAMG_all_stations.values[~np.isnan(ZAMG_all_stations.values)]
x = np.linspace(data.min(), data.max(), 100)

n, bins, patches = plt.hist(data,bins=x, normed=True)



#param = ss.exponweib.fit(data, floc=0)
#
#pdf_fitted = ss.exponweib.pdf(data, *param[:-2], loc=param[-2], scale=param[-1]) #* len(x)
#plt.plot(pdf_fitted, label='eib')


import matplotlib.pyplot as plt
import scipy
import scipy.stats

size = len(data)
x = np.linspace(data.min(), data.max(), 100)
y = data
h = plt.hist(y, bins=range(50), color='w', log=True)

# dist_names = ['gamma', 'beta', 'rayleigh', 'norm', 'pareto']
dist_names = ['pareto', 'weibull_min', 'lognorm', 'gamma']

fig = plt.figure()
ax = fig.add_subplot(1,1,1)  
ax.hist(y, bins=60, color='g', log=True)
# ax.hist(y, bins=range(50), color='w')

for dist_name in dist_names:
    dist = getattr(scipy.stats, dist_name)
    param = dist.fit(y, loc=0)
    pdf_fitted = dist.pdf(x, *param[:-2], loc=param[-2], scale=param[-1]) * size
  
    ax.plot(pdf_fitted, label=dist_name)
    #ax.set_yscale('log')
plt.xlim(0,50)
plt.legend(loc='upper right')
plt.show()
'''
-------------------------------
--------------new--------------
-------------------------------
'''
# -------------------------------------------------------------------
treegreen = .1, .999, .1
pink = .9, 0, .9
light_coral = 0.9375, 0.5000, 0.5000
medium_orchid = 0.7266, 0.3320, 0.8242
# -------------------------------------------------------------------

size = len(data)
x = np.linspace(data.min(), data.max(), 100)
y = data
counts,binEdges = np.histogram(data,bins=60, density=True)
bin_centres = 0.5*(binEdges[1:]+binEdges[:-1])
width = 0.7 * (binEdges[1] - binEdges[0])

# dist_names = ['gamma', 'beta', 'rayleigh', 'norm', 'pareto']
dist_names = ['pareto', 'weibull_min', 'lognorm']

fig = plt.figure()
fig.suptitle("ZAMG 10min precipitation", fontsize=10)
ax = fig.add_subplot(1,1,1)  
#ax.hist(y, bins=60, color='g', log=True)
ax.set_xlabel('intensity [mm/10min]', fontsize=8)
plt.tick_params(axis='both', which='major', labelsize=8)
plt.bar(bin_centres, counts, align='center', width=width, edgecolor='None',
        color=treegreen)
#ax.set_yscale('log')
# ax.hist(y, bins=range(50), color='w')

for dist_name in dist_names:
    dist = getattr(scipy.stats, dist_name)
    param = dist.fit(y, loc=0)
    #param = dist.fit(y)
    pdf_fitted = dist.pdf(x, *param[:-2], loc=param[-2], scale=param[-1]) * size
  
    ax.plot(pdf_fitted, label=dist_name)
    ax.set_yscale('log')
plt.xlim(0,50)
plt.legend(loc='upper right')
plt.show()






