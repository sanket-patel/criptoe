import pandas as pd
import pigeon
import numpy as np
import time
import datetime as dt
import json
import threading
import buffer
import collections


# does stats on incoming data from redis server
# and pushes it back on interval
#
# also can eventually grab data from database


# each statistic requires it's own key which data is collected from
# in case that some strategy exists which requires data from multiple channels
# for different statistics

class census:

    # general functions to set up class and handle data

    def __init__(self, sbus, key, max_size=1000):
        self.schoolbus = sbus
        self.messenger = pigeon.pigeon(self.schoolbus)
        self.key = key
        self.messages = collections.deque([], max_size)
        self.stopper = threading.Event()


    def get_stats_thread(self, pubkey, stats, interval, **kwargs):
        listener = threading.Thread(target=self.begin)
        listener.start()
        while not self.stopper.is_set():
            packaged_data = self.package(stats, **kwargs)
            self.pub(pubkey, packaged_data)
            time.sleep(interval)

    def get_stats(self, pubkey, stats, interval, **kwargs):
        statargs = (pubkey, stats, interval)
        threading.Thread(target=self.get_stats_thread, args=statargs, kwargs=kwargs).start()

    def stop(self):
        self.stopper.set()

    def begin(self):
        self.messenger.sub('schoolbus', self.key)
        for msg in self.messenger.sublisten():
            self.messages.append(msg)



    # publishes package of data into server
    def pub(self, pubkey, data):
        self.schoolbus.publish(pubkey, data)

    # packages data into a single dict ready to publish to redis server
    def package(self, stats, **kwargs):
        while len(self.messages) < 1:
            continue
        current_messages = list(self.messages)
        data = {}
        if 'moving_average' in stats:
            num_msg = kwargs.get('ma_num_msg')
            data['moving_average'] = self.moving_average(current_messages, num_msg)
        return data

    # statistic functions

    # zscore as general function in case other statistics need it
    def zscore(self, data):
        avg = np.mean(data, axis=1, keepdims=True)
        stdev = np.std(data, axis=1, keepdims=True)
        zscores = (data-avg) / stdev
        return zscores

    # generates moving average after each incoming message using last num_msg
    # pieces of data
    #
    # outputs a dict of average price and time of last trade used in calc
    def moving_average(self, msgs, num_msg):
        if not isinstance(num_msg, list):
            num_msg = [num_msg]
        all_mov_avg = {}
        for cap in num_msg:
            queue = collections.deque([], cap)
            [queue.append(json.loads(item['data'])) for item in msgs]
            prices = pd.DataFrame(list(queue))
            avg_price = prices['price'].apply(float).mean()
            last_time = queue[-1]['time']
            all_mov_avg[f'{cap}_mavg'] = {'avg':avg_price, 'time':last_time}
        return all_mov_avg

    def autoregression(self, key, order):
        pass
