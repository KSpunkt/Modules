# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 08:21:18 2015

@author: Kaddabadda
*** read variable from ZAMG Station files to pandas dataframe and save as npy
"""

import Modules.ZAMG_tawes.stationfiles_v9 as zamg
import pandas as pd

print zamg.var_key

def ZAMG_to_npy(var):
    '''INPUT:
    *** var: variable to be read into dataframe, use chiffre from zamg.var_key
    (numbers 1-10)
    '''
    if var<0 or var>10:
        print ' !!! Variable number not valid (chose numbers 1-10) !!!'
        return
    else:
        variable = zamg.var_key.values()[var]
        print 'read ', variable    
    
    emptylist = []
    pth2 = 'I:\DOCUMENTS\WEGC\\02_PhD_research\\03_Data\ZAMG\processed_data\Station_Dataframes' 
    
    for eachStation in zamg.statlist:
        statnr = int(eachStation)
        print 'processing statnr: ', statnr
    
        df = pd.read_csv(pth2 + '\DataFrame_' + str(statnr) + '.csv', index_col=0,
                         usecols=[0,'precip'], parse_dates=True)
    
        # selector extended summer months AMJJASO
        month = df.index.month
        selector = ((1 <= month) & (month <= 12))
        data = df.iloc[:,[0]][selector] #precip[selector]
        data.columns = [eachStation]
        del df
        emptylist.append(data)
    
    ZAMG_all_stations = pd.concat(emptylist, axis=1)
    
    ZAMG_all_stations.to_pickle(pth2 + '\ZAMG_10min_allyear_' + variable +
                                '.npy')

