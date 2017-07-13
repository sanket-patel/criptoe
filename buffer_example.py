import gdax, time
from collections import deque
import buffer as bf

class myWebsocketClient(gdax.WebsocketClient):
    #
    def on_open(self):
        #
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["ETH-USD"]
        self.message_count = 0
        self.sma = bf.Buffer(5)
        self.lma = bf.Buffer(10)
    
    def on_message(self, msg):
        #
        time.sleep(.5)
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            #if msg['type']=='done':
            price = float(msg['price'])
            self.sma.add(price)
            self.lma.add(price)
        print('sma: ', self.sma.moving_average())
        print('lma: ', self.lma.moving_average(), '\n\n')
            
    def on_close(self):
        #
        print("-- Goodbye! --")

wsClient = myWebsocketClient()
wsClient.start()

while wsClient.message_count < 100:
    continue
    
wsClient.close()

