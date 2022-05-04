import time
import datetime
from binance.spot import Spot as Client
import unicorn_binance_websocket_api
import pandas as pd
import matplotlib.pyplot as plt
import json
from threading import Thread

df = pd.DataFrame()

def get_history(df):
    coin = 'BTCUSDT'
    interval = '1m'
    limit = 1000
    dt_start = datetime.datetime(2022,5,4, 12)
    dt_start_ = round(time.mktime(dt_start.timetuple())*1000)

    spot_client = Client(base_url="https://api1.binance.com")
    klines = spot_client.klines(coin, interval, startTime = dt_start_, limit = limit)
    df = pd.DataFrame(klines)
    df.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
    df["Close"] = df.Close.astype(float)
    df.drop(['Open', 'High', 'Low', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore'], axis = 1, inplace = True)
    return df

if __name__ == '__main__':
    plt.ion()
    plt.rcParams['toolbar'] = 'None' 
    ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com")
    ubwa.create_stream('kline_1m', "BTCUSDT")
    jsMessage_last = {'data':'k'}
    jsMessage_last['data'] = {'k':'t', 'k':'c'}
    jsMessage_last['data']['k'] = {'t':0, 'c':0}
    while True:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            jsMessage = json.loads(oldest_data_from_stream_buffer)
            if 'stream' in jsMessage.keys():
                if jsMessage['data']['k']['t'] > jsMessage_last['data']['k']['t']:
                    jsMessage_last = jsMessage
                    df = get_history(df)
                    print()
                    print(df)
                else:
                    # df.iloc[df.last_valid_index()] = pd.DataFrame.from_dict({'Opentime': [jsMessage_last['data']['k']['t']], 'Close': [jsMessage_last['data']['k']['c']]})
                    df.iloc[df.last_valid_index(), 0] = jsMessage['data']['k']['t']
                    df.iloc[df.last_valid_index(), 1] = jsMessage['data']['k']['c']
                    df["Close"] = df.Close.astype(float)
                    
                    plt.clf()
                    plt.plot(df['Opentime'], df['Close'])
                    plt.draw()
                    plt.gcf().canvas.flush_events()
        else: time.sleep(1)