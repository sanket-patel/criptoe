'''
Created on Jul 22, 2017

@author: Sanket
'''

class factory(object):
    ''' Market Data Factor '''
    
    @staticmethod
    def create_feed(exchange, config):
        ''' create a feed to an exchange '''

        exchange = exchange.lower()
        
        if exchange == 'gdax':
            #from feeds.gdax_feed import GdaxFeed
            from feeds import GdaxFeed
            feed = GdaxFeed.GdaxFeed()
        
        elif exchange == 'poloniex':
            from feeds import PoloniexFeed
            feed = PoloniexFeed.PoloniexFeed()

        elif exchange == 'kraken':    
            from feeds import KrakenFeed
            feed = KrakenFeed.KrakenFeed()

        elif exchange == 'bitstamp':
            from feeds import BitstampFeed
            feed = BitstampFeed.BitstampFeed()
        
        else:
            raise Exception('Unknown exchange')

        return feed

    @staticmethod
    def get_available_feeds():
        ''' return all available types '''
        
        return ['gdax', 'poloniex', 'kraken', 'bitstamp']