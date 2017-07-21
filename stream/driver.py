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
    # collects data from exchange
    birdy = pigeon.pigeon(yellowbus, products='BTC-USD')
    birdy.sub(target='client')
    # collects data for specific tag and gets stats on it
    turkey = pigeon.pigeon(sbus=yellowbus)
    turkey.sub(target='schoolbus', key='gdax_btcusd_done')

    turkey.get_stats(['moving_average'], .5, outkey='test', ma_num_msg=[10, 20, 30, 40, 50], max_size=100)

    ear = pigeon.pigeon(yellowbus)
    ear.sub(target='schoolbus', key='test')


    pp = pprint.PrettyPrinter(indent=4)
    [pp.pprint(census.census.decode_data(msg)) for msg in ear.sublisten()]

if __name__ == '__main__':
    main()
