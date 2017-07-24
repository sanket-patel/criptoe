import datetime as dt
import pandas as pd
import messenger
import redis
import time
import threading
import stats
import collections
import pprint

# driver file for tests and what not

def main():
    boring_redis_bus_name = redis.StrictRedis()

    # collects data from exchange
    exchange_stream = messenger.Messenger(boring_redis_bus_name, products='BTC-USD')
    exchange_stream.sub(target='client')

    # collects data for specific tag and gets stats on it
    stats_stream = messenger.Messenger(sbus=boring_redis_bus_name)
    stats_stream.sub(target='schoolbus', key='gdax_btcusd_done')
    stats_stream.get_stats(['moving_average'], .5, outkey='test', ma_num_msg=[10, 20, 30, 40, 50], max_size=100)

    # listens for the stats under 'test' key
    listener = messenger.Messenger(boring_redis_bus_name)
    listener.sub(target='schoolbus', key='test')


    pp = pprint.PrettyPrinter(indent=4)
    [pp.pprint(stats.Stats.decode_data(msg)) for msg in listener.listen_to_stream()]

if __name__ == '__main__':
    main()
