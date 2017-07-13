# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 21:34:59 2017

@author: Sanket
"""

import pandas_talib as ta
import numpy as np
import pandas as pd

class Buffer:
    
    def __init__(self, size):
        #
        self.size    = size
        self.frame   = None
        self._count  = 0
        self.create_frame()
        
    def create_frame(self):
        #
        arr        = np.empty([self.size,1])
        self.frame = pd.DataFrame(arr, columns=['values'])
        
    def add(self, value):
        #
        self._count = self._count + 1
        self.frame.iloc[0:-1] = self.frame[1:].values
        self.frame.iloc[-1]   = value
        
    def moving_average(self):
        #
        if self._count >= self.size:
            ma = ta.MA(self.frame, self.size, price='values')
            return ma[ma.columns[1]].iloc[-1]
        else:
            return 'not_enough_values'
        

        