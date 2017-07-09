import gdax, time
import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import json


# inherited the class
class webclient(gdax.WebsocketClient):

    def __init__(self, url="wss://ws-feed.gdax.com", products=None, message_type="subscribe"):
        self.url = url
        self.products = products
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
            self.data.typedict[msg_type] = self.data.queuer(msg, self.data.typedict[msg_type], 100)
            # print(self.data.typedict[msg_type])
        # time.sleep(1)

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


    def animate(self, axis, frame):
        prices = [float(x) for x in frame['price']]
        times = frame['time']
        axis.clear()
        axis.set_ylim([2300,2700])
        axis.set_autoscaley_on(False)
        axis.plot_date(times, prices, xdate=True, ydate=False, color='blue', linestyle='solid', linewidth=2,  markersize=2)


        # based on message type, will return respective dataframe
    def get_frame(self, msg_type):
        return self.typedict[msg_type]


def create_graph(socket, msg_type):
    while len(socket.get_messages().get_frame('done')) < 5:
        time.sleep(1)  # wait for data to be put into this frame

    # graph
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    # updates graph every interval
    param_animate = lambda x: socket.get_messages().animate(ax1, socket.get_messages().get_frame(msg_type))
    animation = ani.FuncAnimation(fig, param_animate, interval=10)
    plt.show()

def main():
    ws = webclient() # open stream
    ws.start()

    create_graph(ws, 'done')
    # x = input()
    # while (x != 'q'): # stall to close socket
    #     x = input()

    ws.close()    # close stream


if __name__ == '__main__':
    main()