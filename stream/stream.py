import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani
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
