'''
Created on Jul 22, 2017

@author: Sanket
'''

from feed_factory import factory
from feeds.GdaxFeed import GdaxFeed, OrderBookConsole
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
    
       
    #gdax_thread = threading.Thread(target=GdaxFeed,args=(md_bus, 'ETH-USD'))
    #gdax_thread.start()
    
    #key = 'gdax_ethusd_done'
    #sub = md_bus.pubsub(ignore_subscribe_messages=True)
    #sub.subscribe(key)
    
    #while True:
    #   for message in sub.listen():
    #        #print('received')
    #        #print(message)
    #        #print('\n')
    #        continue
    bus = redis.StrictRedis()
    
    order_book = OrderBookConsole(product_id='ETH-USD', bus=bus)
    order_book_thread = threading.Thread(target=order_book.start)
    order_book_thread.start()
    
    key = 'order_book'
    sub = bus.pubsub(ignore_subscribe_messages=True)
    sub.subscribe(key)
    
    while True:
        for message in sub.listen():
            message = json.loads(message['data'])                                  
            print('[BID] %s @ %s X [ASK] %s @ %s' % (message['bid'], message['bid_depth'], message['ask'], message['ask_depth']))
            continue
    
if __name__ == '__main__':
    main()