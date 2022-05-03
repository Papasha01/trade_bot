from itertools import count
import time
import datetime
from binance.spot import Spot as Client
import unicorn_binance_websocket_api
import pandas as pd
import matplotlib.pyplot as plt


download_url = ("https://raw.githubusercontent.com/fivethirtyeight/data/master/college-majors/recent-grads.csv")
df = pd.read_csv(download_url)
df.info()
df.plot(x="Rank", y=["P25th", "Median", "P75th"])
plt.show()