# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 12:06:35 2015

@author: Kaddabadda
"""
import pandas as pd

from rpy2.robjects import pandas2ri
pandas2ri.activate()

from rpy2.robjects import r
r.data('prediction')
df_iris = pandas2ri.ri2py(r[prediction])



from rpy2 import robjects

Rdir  = "I:/DOCUMENTS/WEGC/02_PhD_research/03_Data/ZAMG/SPARTACUS/TMAX/rda/Tx20130227.rda"
f = r'/Tx20130227.rda'

obj = Rdir + f

m=robjects.r('matrix(1:6, nrow=2, ncol=3)')

m = robjects.reval(obj)

rdf = 'I:/DOCUMENTS/WEGC/02_PhD_research/03_Data/ZAMG/SPARTACUS/TMAX/rda/Tx20130227.rda'

pandas2ri.ri2py(rdf)



test = pd.read_csv(r'C:\Users\Kaddabadda\Documents\test.csv', 
                   index_col = [0])