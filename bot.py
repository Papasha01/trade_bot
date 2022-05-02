from itertools import count
import time
import datetime
from binance.spot import Spot as Client
import unicorn_binance_websocket_api
import pandas as pd
import matplotlib.pyplot as plt


coin = 'BTCUSDT'
interval = '1m'
limit = 1000
dt_start = datetime.datetime(2022,5,1,12)
dt_start_ = round(time.mktime(dt_start.timetuple())*1000)

spot_client = Client(base_url="https://api1.binance.com")
klines = spot_client.klines(coin, interval, startTime = dt_start_, limit = limit)

df = pd.DataFrame()
df2 = pd.DataFrame(klines)
df2.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
df = pd.concat([df2, df], axis=0, ignore_index=True, keys=None)

plt.plot(df["Close"], df["Closetime"])
plt.show()