import unicorn_binance_websocket_api
from binance.client import Client
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json
from threading import Thread
from progress.spinner import Spinner
from decimal import Decimal

D = Decimal

def create_stop_loss():
    try:
        info = client.futures_exchange_info()
        for x in info['symbols']:
            if x['symbol'] == coin:
                pricePrecision = x['pricePrecision']
        x = client.futures_account()['positions']
        for i in x:
            if i['symbol'] == coin and i['positionAmt'] != '0':
                if float(i['positionAmt']) > 0:
                    client.futures_create_order(
                    symbol=coin,
                    type='STOP_MARKET',
                    side='SELL',
                    stopPrice=Decimal(i['entryPrice'])-D(stop_loss*0.1**pricePrecision).quantize(D("1.000000")),
                    closePosition=True
                    )
                elif float(i['positionAmt']) < 0:
                    client.futures_create_order(
                    symbol=coin,
                    type='STOP_MARKET',
                    side='BUY',
                    stopPrice=Decimal(i['entryPrice'])+D(stop_loss*0.1**pricePrecision).quantize(D("1.000000")),
                    closePosition=True
                    )
    except Exception as e:
        print(e)
        if e == 'APIError(code=-2021): Order would immediately trigger.':
            close_pozition()
        time.sleep(5)
        create_stop_loss()

def poz_short():
    try:
        close_pozition()
        client.futures_create_order(symbol=coin, side='SELL', type='MARKET', quantity=position_amount)
        create_stop_loss()
        print(str(datetime.datetime.now()) + ' short')
    except Exception as e:
        print(e)
        time.sleep(5)
        poz_short()

def poz_long():
    try:
        close_pozition()
        client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=position_amount)
        create_stop_loss()
        print(str(datetime.datetime.now()) + ' long')
    except Exception as e:
        print(e)
        time.sleep(5)
        poz_long()

def close_pozition():
    try:
        x = client.futures_account()['positions']
        for i in x:
            if i['symbol'] == coin and i['positionAmt'] != '0':
                if float(i['positionAmt']) > 0:
                    order = client.futures_create_order(symbol=coin, side='SELL', type='MARKET', quantity=abs(float(i['positionAmt'])))
                    # print(f"SELL: {order}")
                elif float(i['positionAmt']) < 0:
                    order = client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=abs(float(i['positionAmt'])))
                    # print(f"BUY: {order}")
    except Exception as e:
        print(e)
        time.sleep(5)
        close_pozition()

def close_unprofitable_positions():
    try:
        x = client.futures_account()['positions']
        for i in x:
            if i['symbol'] == coin and i['positionAmt'] != '0' and float(i['unrealizedProfit']) < -stop_loss:
                if float(i['positionAmt']) > 0:
                    order = client.futures_create_order(symbol=coin, side='SELL', type='MARKET', quantity=abs(float(i['positionAmt'])))
                    print(f"SELL: {order}")
                elif float(i['positionAmt']) < 0:
                    order = client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=abs(float(i['positionAmt'])))
                    print(f"BUY: {order}")
    except Exception as e:
        print(e)
        time.sleep(5)
        close_unprofitable_positions()

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

def get_history():
    try:
        klines = client.get_klines(symbol=coin, limit = limit, interval = interval)
        df = pd.DataFrame(klines)
        df.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
        df["Close"] = df.Close.astype(float)
        df.drop(['Open', 'High', 'Low', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore'], axis = 1, inplace = True)
        average("MA1", length_MA1, df)
        average("MA2", length_MA2, df)
        return df
    except Exception as e:
        print(e)
        time.sleep(5)
        get_history()

def enter_api_key():
    try:
        client = Client(
        api_key = '9YFuTICk3DzXd7PYVyJA9BgOXM1ktEjfIbEhVZoy2FcgNwbdi2V0zzAzYPJ4DbkO', 
        api_secret = 'xLkCdvdWvwQ2ZMKNQTZwz1HjKEUGq2VtFfO0nhWRmzsRARbixO1jmszFDXvuvOGi')
        return client
    except Exception as e:
        print(e)
        time.sleep(5)

def get_position_amount():
    try:
        balance = client.futures_account_balance()
        for i in balance:
            if i['asset'] == 'USDT':
                trade_balance = float(i['balance']) * trading_ratio
        coin_price = client.get_symbol_ticker(symbol = coin)
        return round(trade_balance/float(coin_price['price']))
    except Exception as e:
        print(e)
        time.sleep(5)
        get_position_amount()

def get_price_poz_top_cp():
    
    if df['MA1'].iloc[length_MA2] > df['MA2'].iloc[length_MA2]:
        return True
    else: 
        return False

def get_price_poz_top():
    if df['MA1'].iloc[len(df.index)-1] > df['MA2'].iloc[len(df.index)-1]:
        return True
    else: 
        return False

def check_profit(length_MA1, length_MA2):
    last_long = Decimal("0")
    last_short = Decimal("0")
    first = True
    profit_point = Decimal("0")
    profit_proc = Decimal("0")

    price_poz_top_cp = get_price_poz_top_cp()

    #print(price_poz_top_cp)
    for i in range(length_MA2-1, df.shape[0]-1):
        if price_poz_top_cp == False:
            if df['MA1'].iloc[i] > df['MA2'].iloc[i]:
                if first == True:
                    last_long = Decimal(df['Close'].iloc[i])
                    price_poz_top_cp = True
                    first = False
                else:
                    #print(-(Decimal(df['Close'].iloc[i]) - last_short))
                    #print(Decimal(df['Close'].iloc[i])/last_short-1)
                    profit_proc -= Decimal(df['Close'].iloc[i])/last_short-1
                    profit_point -= Decimal(df['Close'].iloc[i]) - last_short
                    last_long = Decimal(df['Close'].iloc[i])
                    price_poz_top_cp = True
        elif price_poz_top_cp == True:
            if df['MA1'].iloc[i] < df['MA2'].iloc[i]:
                if first == True:
                    last_short = Decimal(df['Close'].iloc[i])
                    price_poz_top_cp = False
                    first = False
                else:
                    #print(Decimal(df['Close'].iloc[i]) - last_long)
                    #print(Decimal(df['Close'].iloc[i])/last_long-1)
                    profit_proc += Decimal(df['Close'].iloc[i])/last_long-1
                    profit_point += Decimal(df['Close'].iloc[i]) - last_long
                    last_short = Decimal(df['Close'].iloc[i])
                    price_poz_top_cp = False
    return profit_proc, profit_point

def check_all_profit():
    for MA1 in range(1, 4):
        for MA2 in range(2, 15):
            average("MA1", MA1, df)
            average("MA2", MA2, df)
            
            profit_proc, profit_point = check_profit(MA1, MA2)
            f = open('profit.txt', 'a+')
            f.write(f"MAs:, {MA1}, {MA2}\n")
            f.write(f"profit: {round(profit_proc*100, 2)}% \n")
            f.write(f"profit: {round(profit_point, 5)} points\n")
            f.write("\n")
            f.close()
            print('MAs:', MA1, MA2)
            print('profit: ', round(profit_proc*100, 2), '%')
            print('profit: ', round(profit_point, 5), 'points')

if __name__ == '__main__':
    spinner = Spinner('Checking ')
    client = None
    while client == None:
        client = enter_api_key()

    # Settings
    coin = 'MANAUSDT'
    length_MA1 = 3
    length_MA2 = 30
    stop_loss = 50          #in points
    trading_ratio = 0.08    #in %
    interval = '1m'
    limit = 200            #max 1000 and > length_MA2
    
    # Объявление DataFrame
    df = pd.DataFrame()

    # Настройка графика
    plt.ion()
    #plt.rcParams['toolbar'] = 'None' 

    # Словарь предыдущей записи
    jsMessage_last = {
        'data':{
            'k':{
                't':0,
                'c':0
            }
        }
    }

    # # Проверка убыточных сделок
    # close_unprofitable_positions()

    # Установка размера позиции
    #position_amount = get_position_amount()

    # Определение положения скользящих
    #price_poz_top = get_price_poz_top()

    # Проверка прибыльности на паре
    # Получение истории цен с подсчетом средних скользящих
    df = get_history()
    
    check_all_profit()

    # Отображение графика
    #buil_graf()
    #plt.show(block=True)

    # # Websocket
    # ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com")
    # ubwa.create_stream(f"kline_{interval}", coin)
    # while True:
    #     oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
    #     if oldest_data_from_stream_buffer:
    #         jsMessage = json.loads(oldest_data_from_stream_buffer)
    #         if 'stream' in jsMessage.keys():
    #             if jsMessage['data']['k']['t'] > jsMessage_last['data']['k']['t']:
    #                 jsMessage_last = jsMessage
    #                 df = get_history()

    #                 if price_poz_top == False:
    #                     if df['MA1'].iloc[len(df.index)-1] > df['MA2'].iloc[len(df.index)-1]:
    #                         print('long')
    #                         #poz_long()
    #                         price_poz_top = True
    #                 elif price_poz_top == True:
    #                     if df['MA1'].iloc[len(df.index)-1] < df['MA2'].iloc[len(df.index)-1]:
    #                         print('short')
    #                         #poz_short()
    #                         price_poz_top = False
    #             else:
    #                 df.iloc[df.last_valid_index(), 0] = jsMessage['data']['k']['t']
    #                 df.iloc[df.last_valid_index(), 1] = jsMessage['data']['k']['c']
    #                 df["Close"] = df.Close.astype(float)

    #                 average_last('MA1', length_MA1, df)
    #                 average_last('MA2', length_MA2, df)
    #                 buil_graf()

    #     else: 
    #         spinner.next()
    #         time.sleep(0.5)