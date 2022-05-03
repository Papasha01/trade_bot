import json
import threading
import websocket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

TRADE_SYMBOL = "ETHUSDT"
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
closes = np.array([])

def on_message(ws, message):
    global closes
    message = json.loads(message)
    candle = message['k']
    close = candle['c']
    closes = np.append(closes, float(close))

def wsthread(closes):
    ws = websocket.WebSocketApp(SOCKET, on_message=on_message)
    ws.run_forever()

t = threading.Thread(target=wsthread, args=(closes,))
t.start()

fig, ax = plt.subplots()
plt.axis([0, 100, 0, 35000])
x= np.arange(100)
y=[np.nan] * 100
line, = ax.plot(x, y)

def animate(i):
    global y
    # shift left to most recent 100 closing prices
    y[:len(closes)] = closes[-100:]
    line.set_ydata(y)
    return line,

def init():
    line.set_ydata([np.nan] * 100)
    return line,

anim = FuncAnimation(
    fig, animate, interval=20,
    init_func=init,
    blit=True
)

plt.show()
