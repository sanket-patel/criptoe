import datetime as dt
import pandas as pd
import pigeon
import redis
import time
import redis

# driver file for tests and what not

def main():
    yellowbus = redis.StrictRedis()

    birdy = pigeon.pigeon(yellowbus, 'BTC-USD')
    birdy.sub(target='client')

    turkey = pigeon.pigeon(yellowbus, 'BTC-USD')
    turkey.sub(target='schoolbus')

    [print(i['data']) for i in turkey.sublisten() if i['type'] == 'message']


if __name__ == '__main__':
    main()
