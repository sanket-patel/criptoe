import numpy as np
import pandas as pd

class Buffer:

    def __init__(self, size, frame=None):
        #
        self.size    = size
        self.frame   = frame
        self._count  = 0
        if self.frame == None:
            self.create_frame()
    def create_frame(self):
        #
        arr        = np.empty([self.size,1])
        self.frame = pd.DataFrame(arr, columns=['values'])

    def get_frame(self):
        return self.frame

    def add(self, value):
        #
        self._count = self._count + 1
        self.frame.iloc[0:-1] = self.frame[1:].values
        self.frame.iloc[-1]   = value

    def moving_average(self):
        #
        if self._count >= self.size:
            ma = pd.Series(pd.rolling_mean(self.frame['values'], self.size))
            return ma.iloc[-1]
        else:
            return 'not_enough_values'
