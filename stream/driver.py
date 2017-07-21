import datetime as dt
import pandas as pd
import pigeon
import redis
import time
import redis
import threading
import census
import collections
import pprint

# driver file for tests and what not

def main():
    yellowbus = redis.StrictRedis()
    birdy = pigeon.pigeon(yellowbus, 'BTC-USD')
    birdy.sub(target='client')

    stats = census.census(yellowbus, 'gdax_btcusd_done')
    stats.get_stats('test', ['moving_average'], .5, ma_num_msg=[10, 100, 1000])

    turkey = pigeon.pigeon(yellowbus)
    turkey.sub(target='schoolbus', key='test')
    pp = pprint.PrettyPrinter(indent=4)
    [pp.pprint(turkey.decode_data(msg)) for msg in turkey.sublisten()]

if __name__ == '__main__':
    main()
