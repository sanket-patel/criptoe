import redis
import webclient
import buffer
import json
import psycopg2
import gdax
import time

class pigeon(gdax.WebsocketClient):
    # pulls messages from 'client' and publishes to 'bus'
    # or subscribes to messages from 'bus' and publishes to DB
    def __init__(self, sbus, products=None, url='wss://ws-feed.gdax.com', \
                message_type='subscribe', exchange='gdax', database=None):
        self.url = url
        self.products = products
        self.type = message_type
        self.stop = False
        self.ws = None
        self.thread = None
        self.exchange = exchange
        self.schoolbus = sbus
        self.database = database
        self.hoagie = self.schoolbus.pubsub()


    def on_message(self, msg):
        key = self.get_exchange() + '_' +  self.get_products() + '_' +  msg['type']
        self.pub(msg, 'schoolbus', key)

    def pub(self, message, target, key=None):
        if target == 'schoolbus':
            self.schoolbus.publish(key, json.dumps(message))
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

    def sub(self, target, key='gdax_btcusd_done'):
        if target == 'client':
            self.start()
        elif target == 'schoolbus':
            self.hoagie.subscribe(key)

    # retreival functions
    def get_exchange(self):
        return self.exchange

    def get_products(self):
        return ''.join(''.join(self.products).split('-')).lower()

    def get_pubsub(self):
        return self.hoagie.get_message()
