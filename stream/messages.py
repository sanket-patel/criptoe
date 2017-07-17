import pandas as pd
import matplotlib.pyplot as plt

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
