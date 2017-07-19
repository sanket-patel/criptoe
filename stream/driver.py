import datetime as dt
import pandas as pd
import pigeon
import redis


def main():
    yellowbus = redis.StrictRedis()

    birdy = pigeon.pigeon(yellowbus, 'BTC-USD')
    birdy.sub(target='client')

    turkey = pigeon.pigeon(yellowbus, 'BTC-USD')
    turkey.sub(target='schoolbus')

    while True:
        turkey.get_pubsub()

if __name__ == '__main__':
    main()
