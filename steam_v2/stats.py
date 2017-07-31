import pandas as pd
import messenger
import numpy as np
import time
import datetime as dt
import threading
import collections
import statsmodels.tsa as smt
import ast
import codecs

# does stats

class Stats:

    ###### general functions #######

    ###### statistics functions ######
    # zscore as general function in case other statistics need it
    def zscore(self, data):
        avg = np.mean(data, axis=1, keepdims=True)
        stdev = np.std(data, axis=1, keepdims=True)
        zscores = (data-avg) / stdev
        return zscores

    # generates moving using last num_msg provided
    def moving_average(self, data, num_msg):
        queue = collections.deque(data, num_msg)
        return list(queue).apply(float).mean()

    # not sure what it does yet; using prebuilt functions
    def arma(self, data, times, orders):
        # created the object with proper variables
        model = smt.arima_model.ARMA(data, orders, dates=times)
        return model.fit(full_output=True, disp=-1)

    def arima(self, data, times, orders):
            model = smt.arima_model.ARIMA(data, orders, dates=times)
            return model.fit(full_output=True, disp=-1)
            # performs adfuller test on data to see if there is
    def adfuller(self, data, maxlag=None, regression='c', autolag='AIC', store=False, regresults=False):
            results = smt.stattools.adfuller(data, maxlag=None, regression='c', autolag='AIC', store=False, regresults=False)
            return results

        ###### utilities ######
    # static function for decoding byte data to a dictionary
    @staticmethod
    def decode_data(msg):
        return ast.literal_eval(codecs.decode(msg['data']))
