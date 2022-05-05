import unicorn_binance_websocket_api
from binance.client import Client
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json
from threading import Thread

def poz_short():
    f = open('python-binance.txt', 'w+')
    x = client.futures_account()['positions']
    for i in x:
        if float(i['positionAmt']) > 0:
            f.write("\n" + str(i))
    print('short')

def poz_long():
    
    print('long')

def average_last(ma_string, length_MA_int, df_klines):
        sum = 0
        for i in range(length_MA_int):
            sum += df_klines['Close'].iloc[len(df_klines.index)-1-i]
            if i >= length_MA_int-1:
                df_klines.loc[len(df_klines.index)-1, ma_string] = sum/length_MA_int

def average(ma_string, length_MA_int, df_klines):
    sum = 0
    x = 0
    df_klines[ma_string] = df_klines['Close'].iloc[0]
    for i, row in enumerate(df_klines['Close'], start = 0):
        sum += row
        if i >=length_MA_int-1:
            df_klines.loc[i, ma_string] = sum/length_MA_int
            sum -= df_klines['Close'].iloc[x]
            x+=1

def buil_graf():
    plt.clf()
    plt.plot(df['Opentime'], df['MA1'])
    plt.plot(df['Opentime'], df['MA2'])
    plt.draw()
    plt.gcf().canvas.flush_events()

def get_history(df, coin, limit, interval):
    klines = client.get_klines(symbol=coin, limit = limit, interval = interval)
    df = pd.DataFrame(klines)
    df.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
    df["Close"] = df.Close.astype(float)
    df.drop(['Open', 'High', 'Low', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore'], axis = 1, inplace = True)
    average("MA1", length_MA1, df)
    average("MA2", length_MA2, df)
    return df

if __name__ == '__main__':

    client = Client(
    api_key = '9YFuTICk3DzXd7PYVyJA9BgOXM1ktEjfIbEhVZoy2FcgNwbdi2V0zzAzYPJ4DbkO', 
    api_secret = 'xLkCdvdWvwQ2ZMKNQTZwz1HjKEUGq2VtFfO0nhWRmzsRARbixO1jmszFDXvuvOGi')

    # Объявление переменных
    length_MA1 = 3
    length_MA2 = 100
    coin = 'BTCUSDT'
    interval = '30m'
    limit = 1000
    df = pd.DataFrame()
    top = True


    # Настройка графика
    plt.ion()
    plt.rcParams['toolbar'] = 'None' 

    # Словарь предыдущей записи
    jsMessage_last = {
        'data':{
            'k':{
                't':0,
                'c':0
            }
        }
    }

    # Websocket
    ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com")
    ubwa.create_stream(f"kline_{interval}", coin)
    while True:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            jsMessage = json.loads(oldest_data_from_stream_buffer)
            if 'stream' in jsMessage.keys():
                if jsMessage['data']['k']['t'] > jsMessage_last['data']['k']['t']:
                    jsMessage_last = jsMessage
                    df = get_history(df, coin, limit, interval)
                else:
                    df.iloc[df.last_valid_index(), 0] = jsMessage['data']['k']['t']
                    df.iloc[df.last_valid_index(), 1] = jsMessage['data']['k']['c']
                    df["Close"] = df.Close.astype(float)


                    average_last('MA1', length_MA1, df)
                    average_last('MA2', length_MA2, df)
                    buil_graf()

                    if top == False:
                        # print()
                        # print(df['MA1'].iloc[len(df.index)-1])
                        # print(df['MA2'].iloc[len(df.index)-1])
                        if df['MA1'].iloc[len(df.index)-1] > df['MA2'].iloc[len(df.index)-1]:
                            poz_long()
                            top = True
                    elif top == True:
                        if df['MA1'].iloc[len(df.index)-1] < df['MA2'].iloc[len(df.index)-1]:
                            poz_short()
                            top = False
        else: time.sleep(1)