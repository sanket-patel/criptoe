import gdax, time
import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import json


# inherited the class
class webclient(gdax.WebsocketClient):

    def on_open(self):
        # enter markets in list of AAA-BBB,CCC-DDD (no spaces)
        # self.products = input('Enter market(s):  ').split(',')
        # self.url = input('Enter exchange: ')
        self.url = 'wss://ws-feed.gdax.com/'
        self.products = ['BTC-USD']
        self.message_count = 0
        self.done = pd.DataFrame()
        self.received = pd.DataFrame()
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:

            values = np.array(list(msg.values()))
            values = values.reshape(1,len(values))

            # print(values.shape)s
            keys = np.array(list(msg.keys()))
            # print (keys.shape)
            print (pd.DataFrame(data=values, columns=keys, index=None))
            time.sleep(1)




# def animate(axis, lt, st):
    # print(lt.columns.values)

    # prices = map(float, lt.['price'])
    # times = list(range(1, len(prices) + 1))
    # ax1.clear()
    # ax1.plot(prices,times)




def main():
    # open stream

    ws = webclient()
    ws.start()

    # fig = plt.figure()
    # ax1 = fig.add_subplot(1,1,1)

    # param_animate = lambda x: animate(ax1, ws.long_term, ws.short_term)
    # animation = ani.FuncAnimation(fig, param_animate, interval=1000)
    # plt.show()


    # stall to close socket
    x = input()
    # close stream

    while (x != 'q'):
        x = input()
    ws.close()


if __name__ == '__main__':
    main()