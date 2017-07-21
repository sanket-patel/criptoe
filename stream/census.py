import pandas as pd
import pigeon
import numpy as np
import time
import datetime as dt
import json
import threading
import buffer
import collections
import statsmodels.tsa as smt
import ast
import codecs

# does stats on incoming data from redis server
# and pushes it back on interval
#
# also can eventually grab data from database


# each statistic requires it's own key which data is collected from
# in case that some strategy exists which requires data from multiple channels
# for different statistics

class census:

    ###### general functions #######
    # packages data into a single dict ready to publish to redis server
    def package(self, stats, messages, **kwargs):
        current_messages = list(messages)
        data = {}
        if 'moving_average' in stats:
            num_msg = kwargs.get('ma_num_msg')
            data['moving_average'] = self.moving_average(current_messages, num_msg)
        return data


    ###### statistics functions ######
    # zscore as general function in case other statistics need it
    def zscore(self, data):
        avg = np.mean(data, axis=1, keepdims=True)
        stdev = np.std(data, axis=1, keepdims=True)
        zscores = (data-avg) / stdev
        return zscores

    # generates moving average after each incoming message using last num_msg
    # pieces of data; outputs a dict of average price and time of last trade used in calc
    def moving_average(self, msgs, num_msg):
        if not isinstance(num_msg, list):
            num_msg = [num_msg]
        all_mov_avg = {}
        for cap in num_msg:
            queue = collections.deque([], cap)
            [queue.append(self.decode_data(item)) for item in msgs]
            prices = pd.DataFrame(list(queue))
            avg_price = prices['price'].apply(float).mean()
            last_time = queue[-1]['time']
            all_mov_avg[f'{cap}_mavg'] = avg_price
            all_mov_avg['time'] =last_time
        return all_mov_avg
    # not sure what it does yet; using predbuilt functions
    def autoregression(self, messages, order):
        data = [decode_data(msg) for msg in messages]
        prices = data['price']
        times = data['time']
        # created the object with proper variables
        stm.arima_model.ARMA(price, order, dates=times)


    ###### utilities ######
    # static function for decoding byte data to a dictionary
    @staticmethod
    def decode_data(msg):
        return ast.literal_eval(codecs.decode(msg['data']))
