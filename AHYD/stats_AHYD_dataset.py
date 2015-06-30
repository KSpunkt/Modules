# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 08:38:03 2015

@author: Kaddabadda
statistics of AHYD dataset
"""
import pandas as pd
import numpy as np
import csv as csv
import locale
pth = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD\Tagessummen'
src = r'I:\DOCUMENTS\WEGC\02_PhD_research\03_Data\AHYD'


AHYD_all = pd.read_pickle(src + '\AHYD_dailysums.npy')

month = AHYD_all.index.month
selector = ((4 <= month) & (month <= 10))
data = AHYD_all[selector]


data.to_pickle(src + '\AHYD_allstations_summer.npy')



data.describe()
# how many valid records per station:
data.count(0)
# how many valid records per date
data.count(1)


# records / number of total daily sums in summer sample
total_sum = data.count(0).sum()

# DRIZZLE
drizzle_selector = (data < 0.2) & (data > 0)
drizzle_precip = data[drizzle_selector]
total_drizzle_days = drizzle_precip.count(0).sum()
# percentage of drizzle < 0.19mm/10min

# DRY DAYS
zero_selector = data==0
drydays = data[zero_selector]
total_drydays = drydays.count(0).sum()

# MISSING VALUES
nan_selector = pd.isnull(data)
nan_precip = data[nan_selector]
total_nan = nan_precip.count(0).sum()

# PRECIP GREATER 0.1mm/day
mm_selector = data > 0.1
total_02mm = data[mm_selector]
total_wet_days = total_02mm.count(0).sum()

perc_wet = np.float(total_wet_days)/np.float(total_sum) * 100.0

perc_drizzle = np.float(total_drizzle_days)/np.float(total_sum) * 100.0

perc_dry = np.float(total_drydays)/np.float(total_sum) * 100.0

greater100 = data[data>100]
greater100 = greater100.dropna(how='all')

# gives for each date the station that had the highest value for the day
data.idxmax(axis=1)

# for each station the date where the station had its max
data.idxmax(axis=0)







