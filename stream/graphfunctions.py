import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani

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
