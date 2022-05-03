from itertools import count
import time
import datetime
from binance.spot import Spot as Client
import unicorn_binance_websocket_api
import pandas as pd
import matplotlib.pyplot as plt


coin = 'BTCUSDT'
interval = '1d'
limit = 1000
dt_start = datetime.datetime(2022,1,1)
dt_start_ = round(time.mktime(dt_start.timetuple())*1000)

spot_client = Client(base_url="https://api1.binance.com")
klines = spot_client.klines(coin, interval, startTime = dt_start_, limit = limit)

df = pd.DataFrame(klines)
df.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
df["Close"] = df.Close.astype(float)
df.plot(x="Opentime", y="Close")
print(df.head())
plt.show()