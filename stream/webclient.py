import gdax
import pandas as pd
import messages
import buffer

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

        if self.data.typedict[msg_type].shape[0] == 0:
            self.data.create_frame(msg_type, msg)
        else:
            self.data.typedict[msg_type] = self.data.queuer(msg, self.data.typedict[msg_type], 1000)
            # print(self.data.typedict[msg_type])
        # time.sleep(.2)

    def get_messages(self):
        return self.data
