import redis
import json
import psycopg2
import gdax
import time
import collections
import codecs
import ast
import threading
import census

# pigeon acts as a messenger between databases
# like a carrier pigeon does
#
# can subscribe to stream from exchange or redis server,
# and publish to either redis server or sql database (sql is not done yet)

class pigeon(gdax.WebsocketClient):

    def __init__(self, sbus, products=None, url='wss://ws-feed.gdax.com', \
                message_type='subscribe', exchange='gdax', database=None, **kwargs):
        self.url = url
        self.type = message_type
        self.exchange = exchange
        self.database = database
        self.schoolbus = sbus
        self.products = products
        self.hoagie = self.schoolbus.pubsub(ignore_subscribe_messages=True)
        self.stopper = threading.Event()
        # don't know don't care
        self.stop = False
        self.ws = None
        self.thread = None
        if 'max_size' in kwargs:
            self.messages = collections.deque([], kwargs.get('max_size'))
        else:
            self.messages = collections.deque([], 1000)

    # on message from exchange, formats key and publishes message untouched
    def on_message(self, msg):
        key = self.get_exchange() + '_' +  self.get_products() + '_' +  msg['type']
        self.pub('schoolbus', msg, key)

    def pub(self, target, message, key=None):
        if target == 'schoolbus':
            self.schoolbus.publish(key, message)
        elif target == 'database':
            with connection.cursor() as cursor:
                sql =  f'''
                        INSERT INTO '{tablename}'
                        ({list(message.keys())})
                        VALUES ({list(message.values())})
                        '''
                cursor.execute(sql)

    def make_connection(self):
        connection = psycopg2.connection(host='greenwich8', port=3306, user='nilaypatel', password='Welcome1',
                     db='greenwich8', charset='utf8mb4',cursorclass=psycopg2.cursors.DictCursor)
        self.database = connection

    def sub(self, target, key=None):
        if target == 'client':
            self.start()
        elif target == 'schoolbus':
            self.hoagie.subscribe(key)

    def unsub(self, key=None):
        self.hoagie.unsubscribe(key)

    def issubbed(self):
        return self.hoagie.subscribed

    def sublisten(self):
        return self.hoagie.listen()

    def get_stats(self, stats, interval, outkey, inkey=None, **kwargs):
        def fill_messages():
            for msg in self.sublisten():
                self.messages.append(msg)

        def in_get_stats(outkey, stats, interval, **kwargs):
            ti84 = census.census()
            threading.Thread(target=fill_messages).start()
            while not self.stopper.is_set():
                if len(self.messages) > 0:
                    packaged_data = ti84.package(stats, self.messages, **kwargs)
                    self.pub('schoolbus', packaged_data, outkey)
                    time.sleep(interval)

        get_statsargs = (outkey, stats, interval)
        if not self.issubbed():
            self.sub('schoolbus', inkey)
        # threaded function to keep streams and stats going simultaneously
        threading.Thread(target=in_get_stats, args=get_statsargs, kwargs=kwargs).start()

    def stop(self, key=None):
        self.stopper.set()
        self.unsub(key)

    ###### utilities ######
    # retreival functions
    def get_exchange(self):
        return self.exchange

    def get_products(self):
        if isinstance(self.products, list):
            return ''.join(''.join(self.products).split('-')).lower()
        else:
            return self.products

    def get_submsg(self):
        return self.hoagie.get_message(ignore_subscribe_messages=True)
