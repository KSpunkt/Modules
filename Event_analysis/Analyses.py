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


pd.read(path2 + '/'+ outfile + '_wet_day_event_statistics.npy')
        idx = pd.IndexSlice        
        SumFrame = DayFrame.loc[idx[:], idx[:,'sum']]