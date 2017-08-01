'''
Created on Jul 22, 2017

@author: Sanket
'''

from feed_factory import factory
from feeds.PoloniexFeed import PoloniexFeed

import redis
import threading
import time
import gdax
import datetime
import pandas as pd
import pprint
import json
import ast
import codecs
    
def main():
    
    broker      = redis.StrictRedis()
    plnx_thread = threading.Thread(target=PoloniexFeed,args=(broker, 'USDT_XRP'))
    plnx_thread.start()

    key = 'poloniex_usdt_xrp'
    sub = broker.pubsub(ignore_subscribe_messages=True)
    sub.subscribe(key)

    for message in sub.listen():
        message = json.loads(message['data'])
        print('[%s]\tlast:%s\t\tbid:%s\t\task:%s' % (message['time'], message['last'], message['bid'], message['ask']))
        continue

    
if __name__ == '__main__':
    main()