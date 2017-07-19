import pandas as pd
import pigeon
import numpy as np
import time
import datetime as dt
import json
import threading
import buffer


# does stats on incoming data from redis server
# and pushes it back on interval
#
# also can eventually grab data from database

class census:
    def __init__(self, sbus):
        self.schoolbus = sbus
        self.hoagie = self.schoolbus.newpubsub()
        self.current_average = None

    def packager(self, stats, **kwargs):
        data = {i:None for i in stats}
        if 'moving_average' in stats:
            key = kwargs.get('ma_key')
            num_msg = kwargs.get('ma_num_msg')
            self.moving_average(key, num_msg)
            data['moving_average'] = self.current_average
        return data


    def pub(self, pubkey, data):
        self.schoolbus.publish(pubkey, data)

    def get_stats(self, stats, pubkey, interval, **kwargs):
        data = self.packager(stats, **kwargs)
        self.pub(pubkey, data)

    def moving_average(self, key, num_msg):
        messenger = pigeon.pigeon(sbus=self.schoolbus)
        messenger.sub('schoolbus', key=key)
        prices = np.array()
        for msg in messenger.sublisten()
            if prices.size() == num_msg:
                self.current_average = prices.mean(0)
                prices = prices[1:].append(msg['data']['prices'])
            else:
                prices.append(msg['data']['prices'])
