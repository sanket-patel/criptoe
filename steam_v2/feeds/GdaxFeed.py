'''
Created on Jul 22, 2017

@author: Sanket
'''

import json
import websocket
from threading import Thread

from bintrees import RBTree
from decimal import Decimal
import pickle
from gdax.public_client import PublicClient
from gdax.websocket_client import WebsocketClient

import time
import datetime as dt

class GdaxFeed(object):
    '''
    classdocs
    '''
    def __init__(self, bus, products):
        '''
        Constructor
        '''
        self.bus      = bus
        self.url      = 'wss://ws-feed.gdax.com'
        self.exchange = 'gdax'
        self.products = self.listify(products)
        self.key      = '%s_%s' % (self.exchange, products.lower().replace('-',''))
        self.begin_stream()

    def begin_stream(self):
        #
        self.create_ws_connection()
        self.start()
        while True:
            continue
        
    def listify(self, products):
        #
        if not isinstance(products, list):
            return [products]
        else:
            return products

    def create_ws_connection(self):
        #
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message   = self.on_message,
                                         on_error     = self.on_error,
                                         on_close     = self.on_close)
        self.ws.on_open = self.on_open
        
    def on_open(self, ws):
        #
        print('opening socket connection to gdax for product(s): %s' % self.products)
        sub_params = {'type'       : 'subscribe', 
                      'product_ids': self.products}
        self.ws.send(json.dumps(sub_params))
        
    def on_message(self, ws, message):
        #
        message = json.loads(message)
        self.handle_message(message)
        
    def handle_message(self, message):
        #
        key = '%s_%s' % (self.key, 'done')
        if message['type'] == 'done' and message['reason'] == 'filled':
            if 'price' in message:
                side = 'bot ' if message['side'] == 'sell' else 'sold'
                msg  = '%s\t%s @ %s' % (message['time'], 
                                           side,
                                           message['price'])
                #print(msg)
                self.publish_to_bus(key, message, msg)
                
        #print(key)
        #print(message)
        #self.publish_to_bus(key, msg)
        
    def on_close(self, ws):
        #
        print('closing socket connection to gdax')
        
    def on_error(self, ws):
        #
        print('UH OH!!! SOMETHING WENT WRONG!!!')

    def start(self):
        #
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
        print('thread started')

    def stop(self):
        #
        self.ws.close()
        self.thread.join()
        print('thread joined')
        
    def publish_to_bus(self, key, message, msg):
        #
        print(msg)
        self.bus.publish(key, message)
        #print('published', '\n', key, '\n', message, '\n')
    
    @staticmethod    
    def download_minute_bars(start_time, end_time, frequency=60):
        #
        import datetime
        import gdax
        import time
        import threading
        
        frequency  = 60
        time_end   = end_time
        offset     = datetime.timedelta(minutes=199)
        b          = datetime.timedelta(seconds=frequency)
        client     = gdax.PublicClient()
        all_prices = []
        
        def go():
            te, ts = 0, 0
            for i in range(1,1001):
                
                if i == 1:
                    te = time_end
                else:
                    te = ts
                
                ts          = te-offset
                temp_prices = client.get_product_historic_rates('ETH-USD', start=ts, end=te, granularity=60)
                temp_prices = [ ','.join(map(str, p)) for p in temp_prices ]
                all_prices  = all_prices + temp_prices                         
                time.sleep(.25)
                #print(ts, '  --->   ', te, '\t', len(all_prices))
        
        my_thread = threading.Thread(target=go,args=())
        my_thread.start()
        
        fo = open('history.csv', 'w')
        fo.write('\n'.join(all_prices))
        fo.close()
        

class OrderBook(WebsocketClient):
    
    def __init__(self, product_id='BTC-USD', log_to=None):
        super(OrderBook, self).__init__(products=product_id)
        self._asks = RBTree()
        self._bids = RBTree()
        self._client = PublicClient()
        self._sequence = -1
        self._log_to = log_to
        if self._log_to:
            assert hasattr(self._log_to, 'write')
        self._current_ticker = None

    @property
    def product_id(self):
        ''' Currently OrderBook only supports a single product even though it is stored as a list of products. '''
        return self.products[0]

    def on_message(self, message):
        if self._log_to:
            pickle.dump(message, self._log_to)

        sequence = message['sequence']
        if self._sequence == -1:
            self._asks = RBTree()
            self._bids = RBTree()
            res = self._client.get_product_order_book(product_id=self.product_id, level=3)
            for bid in res['bids']:
                self.add({
                    'id': bid[2],
                    'side': 'buy',
                    'price': Decimal(bid[0]),
                    'size': Decimal(bid[1])
                })
            for ask in res['asks']:
                self.add({
                    'id': ask[2],
                    'side': 'sell',
                    'price': Decimal(ask[0]),
                    'size': Decimal(ask[1])
                })
            self._sequence = res['sequence']

        if sequence <= self._sequence:
            # ignore older messages (e.g. before order book initialization from getProductOrderBook)
            return
        elif sequence > self._sequence + 1:
            print('Error: messages missing ({} - {}). Re-initializing websocket.'.format(sequence, self._sequence))
            self.close()
            self.start()
            return

        msg_type = message['type']
        if msg_type == 'open':
            self.add(message)
        elif msg_type == 'done' and 'price' in message:
            self.remove(message)
        elif msg_type == 'match':
            self.match(message)
            self._current_ticker = message
        elif msg_type == 'change':
            self.change(message)

        self._sequence = sequence

        # bid = self.get_bid()
        # bids = self.get_bids(bid)
        # bid_depth = sum([b['size'] for b in bids])
        # ask = self.get_ask()
        # asks = self.get_asks(ask)
        # ask_depth = sum([a['size'] for a in asks])
        # print('bid: %f @ %f - ask: %f @ %f' % (bid_depth, bid, ask_depth, ask))

    def on_error(self, e):
        self._sequence = -1
        self.close()
        self.start()

    def add(self, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }
        if order['side'] == 'buy':
            bids = self.get_bids(order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['price'], bids)
        else:
            asks = self.get_asks(order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['price'], asks)

    def remove(self, order):
        price = Decimal(order['price'])
        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['order_id']]
                if len(bids) > 0:
                    self.set_bids(price, bids)
                else:
                    self.remove_bids(price)
        else:
            asks = self.get_asks(price)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['order_id']]
                if len(asks) > 0:
                    self.set_asks(price, asks)
                else:
                    self.remove_asks(price)

    def match(self, order):
        size = Decimal(order['size'])
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if not bids:
                return
            assert bids[0]['id'] == order['maker_order_id']
            if bids[0]['size'] == size:
                self.set_bids(price, bids[1:])
            else:
                bids[0]['size'] -= size
                self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if not asks:
                return
            assert asks[0]['id'] == order['maker_order_id']
            if asks[0]['size'] == size:
                self.set_asks(price, asks[1:])
            else:
                asks[0]['size'] -= size
                self.set_asks(price, asks)

    def change(self, order):
        try:
            new_size = Decimal(order['new_size'])
        except KeyError:
            return
            
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is None or not any(o['id'] == order['order_id'] for o in bids):
                return
            index = [b['id'] for b in bids].index(order['order_id'])
            bids[index]['size'] = new_size
            self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if asks is None or not any(o['id'] == order['order_id'] for o in asks):
                return
            index = [a['id'] for a in asks].index(order['order_id'])
            asks[index]['size'] = new_size
            self.set_asks(price, asks)

        tree = self._asks if order['side'] == 'sell' else self._bids
        node = tree.get(price)

        if node is None or not any(o['id'] == order['order_id'] for o in node):
            return

    def get_current_ticker(self):
        return self._current_ticker

    def get_current_book(self):
        result = {
            'sequence': self._sequence,
            'asks': [],
            'bids': [],
        }
        for ask in self._asks:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_ask = self._asks[ask]
            except KeyError:
                continue
            for order in this_ask:
                result['asks'].append([order['price'], order['size'], order['id']])
        for bid in self._bids:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_bid = self._bids[bid]
            except KeyError:
                continue

            for order in this_bid:
                result['bids'].append([order['price'], order['size'], order['id']])
        return result

    def get_ask(self):
        return self._asks.min_key()

    def get_asks(self, price):
        return self._asks.get(price)

    def remove_asks(self, price):
        self._asks.remove(price)

    def set_asks(self, price, asks):
        self._asks.insert(price, asks)

    def get_bid(self):
        return self._bids.max_key()

    def get_bids(self, price):
        return self._bids.get(price)

    def remove_bids(self, price):
        self._bids.remove(price)

    def set_bids(self, price, bids):
        self._bids.insert(price, bids)

class OrderBookConsole(OrderBook):
    ''' Logs real-time changes to the bid-ask spread to the console '''

    def __init__(self, product_id=None, bus=None):
        super(OrderBookConsole, self).__init__(product_id=product_id)

        # latest values of bid-ask spread
        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None
        self.bus = bus

    def on_message(self, message):
        super(OrderBookConsole, self).on_message(message)

        # Calculate newest bid-ask spread
        bid = self.get_bid()
        bids = self.get_bids(bid)
        bid_depth = sum([b['size'] for b in bids])
        ask = self.get_ask()
        asks = self.get_asks(ask)
        ask_depth = sum([a['size'] for a in asks])

        if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
            # If there are no changes to the bid-ask spread since the last update, no need to print
            pass
        else:
            # If there are differences, update the cache
            self._bid = bid
            self._ask = ask
            self._bid_depth = bid_depth
            self._ask_depth = ask_depth
            #print('{}\tbid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f} \t[{:.2f}]'.format(dt.datetime.now(), bid_depth, bid,
            #                                                              ask_depth, ask, ask-bid))
        
        key = 'order_book'
        ob_message = {'bid':float(bid), 
                      'bid_depth':float(bid_depth),
                      'ask':float(ask),
                      'ask_depth':float(ask_depth),
                      'spread':float(ask-bid)}
        self.bus.publish(key, json.dumps(ob_message))

    
        