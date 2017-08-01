import json
import websocket
import pickle
import logging
import time
import datetime

from threading import Thread
from bintrees import RBTree
from decimal import Decimal

logger = logging.getLogger(__name__)
KEYS   = {'USDT_XRP':127}

class PoloniexFeed(object):

    def __init__(self, bus, products):
        #
        self.bus      = bus
        self.exchange = 'poloniex'
        self.products = products
        self.key      = '%s_%s' % (self.exchange, products.lower().replace('-',''))
        self.plnx_key = self.get_key()
        print(self.key)
        self.begin_stream()

    def begin_stream(self):
        #
        self.create_connection()
        self.start()
        while 1:
            continue

    def create_connection(self):\
        #        
        self.ws = websocket.WebSocketApp("wss://api2.poloniex.com/",
                                         on_message = self.on_message,
                                         on_error   = self.on_error,
                                         on_close   = self.on_close)
        self.ws.on_open = self.on_open

    def start(self):
        #
        self.t = Thread(target=self.ws.run_forever)
        self.t.daemon = True
        self.t.start()
        print('Thread started')

    def stop(self):
        #
        self.ws.close()
        self.t.join()
        print('Thread joined')

    def get_key(self):
        #
        return KEYS[self.products]

    def on_message(self, ws, message):
        #
        message = json.loads(message)
        
        if 'error' in message:
            return
        else:
            #print(message)
            self.handle_message(message)

        if message[0] == 1002:
            #
            if message[1] == 1:
                print('Subscribed to ticker')
                return
            if message[1] == 0:
                print('Unsubscribed to ticker')
                return

    def handle_message(self, message):
        #
        if len(message) > 2:
            if message[2][0] == self.plnx_key:
                message = list(map(float, message[2][1:]))
                data    = {'time'        : datetime.datetime.now().isoformat(), 
                           'last'        : message[0],
                           'ask'         : message[1],
                           'bid'         : message[2],
                           '24hr_change' : message[3],
                           '24hr_high'   : message[7],
                           '24hr_low'    : message[8]}
                self.publish_to_bus(data)


    def on_open(self, ws):
        #
        print('Opening socket connection to poloniex')
        self.ws.send(json.dumps({'command': 'subscribe'}))
        self.ws.send(json.dumps({'command':'subscribe','channel':1002}))

    def on_close(self, ws):
        print("Websocket closed!")

    def on_error(self, ws, error):
        print(error)
        
    def publish_to_bus(self, message):
        #
        #print(message)
        self.bus.publish(self.key, json.dumps(message))
