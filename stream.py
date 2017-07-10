import gdax, time
import datetime as dt
import multiprocessing as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import json


# inherited the class
class webclient(gdax.WebsocketClient):

    def __init__(self, url="wss://ws-feed.gdax.com", products=None, message_type="subscribe"):
        self.url = url
        self.products = input('Enter products: ').split(',')
        self.type = message_type
        self.stop = False
        self.ws = None
        self.thread = None
        self.data = messages()


    def on_message(self, msg):
        # adds message to dataframe, or creates dataframe if needed
        msg_type = msg['type']

        if len(self.data.typedict[msg_type]) == 0:
            self.data.create_frame(msg_type, msg)
        else:
            self.data.typedict[msg_type] = self.data.queuer(msg, self.data.typedict[msg_type], 1000)
            # print(self.data.typedict[msg_type])
        # time.sleep(.2)

    def get_messages(self):
        return self.data


class messages:

    def __init__(self):
        self.received_frame              = pd.DataFrame()
        self.done_frame                  = pd.DataFrame()
        self.open_frame                  = pd.DataFrame()
        self.match_frame                 = pd.DataFrame()
        self.change_frame                = pd.DataFrame()
        self.margin_profile_update_frame = pd.DataFrame()
        self.heartbeat_frame             = pd.DataFrame()
        self.error_frame                 = pd.DataFrame()

        self.typedict = {
            'received': self.received_frame,
            'done': self.done_frame,
            'open': self.open_frame,
            'match': self.match_frame,
            'change': self.change_frame,
            'margin': self.margin_profile_update_frame,
            'heartbeat': self.heartbeat_frame,
            'error': self.error_frame
            }


    def create_frame(self, msg_type, msg):
        self.typedict[msg_type] = pd.DataFrame(msg, index=[0])


    def queuer(self, msg, frame, max_size):
        row = pd.DataFrame(msg, index=[0])
        if frame.shape[0] == max_size:
            frame = frame.append(row, ignore_index=True)
            frame = frame.iloc[1:]
        else:
            frame = frame.append(row, ignore_index=True)
        return frame


    def animate(self, axis, frame, ani_min_price, ani_max_price, color):
        prices = [float(x) for x in frame['price']]
        times = frame['time']
        axis.clear()

        axis.set_ylim([ani_min_price, ani_max_price])

        axis.set_autoscaley_on(False)
        axis.set_xlabel('time', fontsize=10)
        axis.set_ylabel('prices', fontsize=10)
        axis.yaxis.grid(color='black', linestyle='-', linewidth=1)
        axis.plot_date(times, prices, xdate=True, ydate=False, color=color, linestyle='solid', linewidth=1,  markersize=1)


        # based on message type, will return respective dataframe
    def get_frame(self, msg_type):
        return self.typedict[msg_type]


def create_graph(socket, msg_type, min_price=0, max_price=3000, color='blue'):
    while len(socket.get_messages().get_frame('done')) < 5:
        time.sleep(1)  # wait for data to be put into this frame

    # graph
    fig = plt.figure()
    fig.suptitle(socket.products[0] + ' ' + msg_type, fontsize=15)

    ax1 = fig.add_subplot(1,1,1)

    # updates graph every interval
    param_animate = lambda x: socket.get_messages().animate(ax1, socket.get_messages().get_frame(msg_type),
                                        min_price, max_price, color)
    animation = ani.FuncAnimation(fig, param_animate, interval=10)
    plt.show()


class historic_data(gdax.PublicClient):
    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days + 1)):
            yield start_date + dt.timedelta(days=n)

    def interday_data(self, start_date, end_date, product, output):
        # NOTE: these dates are inclusive
        start = dt.datetime.strptime(start_date, '%Y-%m-%d')    # start
        end = dt.datetime.strptime(end_date, '%Y-%m-%d')        # end

        with open(output, 'a') as f:
            f.write('time,low,high,open,close,volume\n')            # titles

        for d in self.daterange(start, end):
            data = self.get_product_historic_rates(product, d.isoformat(), \
            (d + dt.timedelta(days=1)).isoformat(), '300')
            print(d)
            with open(output, 'a') as f:
                data = [[str((dt.datetime(1970, 1, 1, 0, 0, 0) + dt.timedelta(seconds=row[0])))] + \
                        [str(item) for item in row[1:]] for row in data]

                [f.write(','.join(line) + '\n') for line in reversed(data)]
    def scheduled_pull(self, interval, granularity, products):
        if not isinstance(products, list):
            products = [products]

        for p in products:
            output_end = p + '_' + (dt.datetime.now()-dt.timedelta(hours=interval)).strftime('%Y-%m-%dT%H:%M:%S')
            output_end = output_end.replace(':', '').replace('-', '')
            outfile = 'M:\\nilay\\criptoe\\historical_data\\%s.csv' % output_end

            with open(outfile, 'a') as f:
                f.write('time,low,high,open,close,volume\n')            # titles

            data = self.get_product_historic_rates(p, (dt.datetime.now()-dt.timedelta(hours=interval, minutes=2)).isoformat(), dt.datetime.now().isoformat(), str(60*granularity))
            with open(outfile, 'a') as f:
                data = [[str((dt.datetime(1970, 1, 1, 0, 0, 0) + dt.timedelta(seconds=int(row[0]))))] + \
                [str(item) for item in row[1:]] for row in data]
                [f.write(','.join(line) + '\n') for line in reversed(data)]


def main():
    hd = historic_data()
    product = 'BTC-USD'
    hd.scheduled_pull(2, 1, product)
    # ws1 = webclient() # open stream
    # ws1.start()
    # create_graph(ws1, 'done')
    # ws1.close()


if __name__ == '__main__':
    main()
