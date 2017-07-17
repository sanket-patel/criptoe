import gdax, time
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani


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
    ws.close()    # close stream


if __name__ == '__main__':
    main()
