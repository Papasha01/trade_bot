from ast import arg
from math import fabs
import unicorn_binance_websocket_api
from binance.client import Client
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json
from threading import Thread
import threading
from progress.spinner import Spinner
from decimal import Decimal
import os

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
                    client.futures_create_order(symbol=coin, side='SELL', type='MARKET', quantity=abs(float(i['positionAmt'])))
                elif float(i['positionAmt']) < 0:
                    client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=abs(float(i['positionAmt'])))
    except Exception as e:
        print(e)
        time.sleep(5)
        close_pozition()

def average_last(ma_string, length_MA_int, df_klines):
        sum = 0
        for i in range(length_MA_int):
            sum += df_klines['Close'].iloc[len(df_klines.index)-1-i]
            if i >= length_MA_int-1:
                df_klines.loc[len(df_klines.index)-1, ma_string] = sum/length_MA_int

def average(ma_string, length_MA_int, df):
    sum = 0
    x = 0
    df[ma_string] = df['Close'].iloc[0]
    for i, row in enumerate(df['Close'], start = 0):
        sum += row
        if i >=length_MA_int-1:
            df.loc[i, ma_string] = sum/length_MA_int
            sum -= df['Close'].iloc[x]
            x+=1

def buil_graf():
    plt.clf()
    plt.plot(df['Opentime'], df['MA1'])
    plt.plot(df['Opentime'], df['MA2'])
    plt.draw()
    plt.gcf().canvas.flush_events()

def get_history(startTime):
    try:
        klines = client.get_klines(symbol=coin, limit = limit, interval = interval, startTime = startTime * 1000) #startTime = 1653177600 * 1000
        df = pd.DataFrame(klines, columns=['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore'])
        df.drop(['Open', 'High', 'Low', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore'], axis = 1, inplace = True)
        df["Close"] = df.Close.astype(float)
        #average("MA3", length_MA3, df)
        return df
    except Exception as e:
        print(e)
        time.sleep(5)
        get_history(startTime)

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
        coin_price = client.get_symbol_ticker(symbol = coin)
        return round(usdt_amount/float(coin_price['price']))
    except Exception as e:
        print(e)
        time.sleep(5)
        get_position_amount()

def get_price_poz_top_cp(df, first_MA, second_MA, index):
    
    if df[first_MA].iloc[index] > df[second_MA].iloc[index]:
        return True
    else: 
        return False

def get_price_poz_top():
    global df
    if df['MA1'].iloc[len(df.index)-2] > df['MA2'].iloc[len(df.index)-2]:
        return True
    else: 
        return False

def check_profit_with_3MA():
    last_long = Decimal("0")
    last_short = Decimal("0")
    first = True,
    commission = Decimal("0.00036") 
    commission_proc = Decimal("0")
    profit_proc = Decimal("0")
    price_top_ma1_ma2 = get_price_poz_top_cp('MA1', 'MA2', length_MA3-1)
    price_top_ma1_ma3 = get_price_poz_top_cp('MA1', 'MA3', length_MA3-1)
    price_top_ma2_ma3 = get_price_poz_top_cp('MA2', 'MA3', length_MA3-1)
    in_poz = False

    for i in range(length_MA3-1, df.shape[0]-1):
        if price_top_ma1_ma3 == True:
            if df['MA1'].iloc[i] < df['MA3'].iloc[i]:
                price_top_ma1_ma3 = False
        elif price_top_ma1_ma3 == False:
            if df['MA1'].iloc[i] > df['MA3'].iloc[i]:
                price_top_ma1_ma3 = True

        if price_top_ma2_ma3 == True:
            if df['MA2'].iloc[i] < df['MA3'].iloc[i]:
                price_top_ma2_ma3 = False
        elif price_top_ma2_ma3 == False:
            if df['MA2'].iloc[i] > df['MA3'].iloc[i]:
                price_top_ma2_ma3 = True

        if price_top_ma1_ma2 == False:
            if df['MA1'].iloc[i] > df['MA2'].iloc[i]:
                price_top_ma1_ma2 = True
                if first == True:
                    if price_top_ma1_ma3 == True and price_top_ma2_ma3 == True:
                        last_long = Decimal(df['Close'].iloc[i])
                        in_poz = True
                        first = False
                else:
                    if in_poz == True:
                        # Продолжение лонга = знак -
                        #print(+(Decimal(df['Close'].iloc[i])/last_short-1)*100)
                        profit_proc -= Decimal(df['Close'].iloc[i])/last_short-1
                        commission_proc -= commission*2
                        in_poz = False
                    elif price_top_ma1_ma3 == True and price_top_ma2_ma3 == True:
                        last_long = Decimal(df['Close'].iloc[i])
                        in_poz = True
                            
        elif price_top_ma1_ma2 == True:
            if df['MA1'].iloc[i] < df['MA2'].iloc[i]:
                price_top_ma1_ma2 = False
                if first == True:
                    if price_top_ma1_ma3 == False and price_top_ma2_ma3 == False:
                        last_short = Decimal(df['Close'].iloc[i])
                        in_poz = True
                        first = False
                else:
                    if in_poz == True:
                        # Продолжение лонга = знак +
                        #print(-(Decimal(df['Close'].iloc[i])/last_long-1)*100)
                        profit_proc += Decimal(df['Close'].iloc[i])/last_long-1
                        commission_proc -= commission*2
                        in_poz = False
                    elif price_top_ma1_ma3 == False and price_top_ma2_ma3 == False:
                        last_short = Decimal(df['Close'].iloc[i])
                        in_poz = True
    return profit_proc, commission_proc

def write_to_file(string, name):
    with open(f'Statistic\{name}.txt', 'a+') as f:
        f.write(str(string) + '\n')

def check_profit(df, MA1, MA2):
    last_long = Decimal("0")
    last_short = Decimal("0")
    first = True
    commission = Decimal("0.00036") 
    commission_proc = Decimal("0")
    profit_proc = Decimal("0")
    
    price_poz_top_cp = get_price_poz_top_cp(df, 'MA1', 'MA2', MA2-1)
    
    #print(price_poz_top_cp)
    for i in range(MA2-1, df.shape[0]-1):
        if price_poz_top_cp == False:
            if df['MA1'].iloc[i] > df['MA2'].iloc[i]:
                price_poz_top_cp = True
                if first == True:
                    last_long = Decimal(df['Close'].iloc[i])
                    first = False
                else:
                    # Продолжение лонга = знак -
                    write_to_file((Decimal(df['Close'].iloc[i])/last_short-1), f'{MA1} {MA2}')
                    profit_proc += Decimal(df['Close'].iloc[i])/last_short-1
                    commission_proc -= commission*2
                    last_long = Decimal(df['Close'].iloc[i])

                    
        elif price_poz_top_cp == True:
            if df['MA1'].iloc[i] < df['MA2'].iloc[i]:
                price_poz_top_cp = False
                if first == True:
                    last_short = Decimal(df['Close'].iloc[i])
                    first = False
                else:
                    # Продолжение лонга = знак +
                    write_to_file(-(Decimal(df['Close'].iloc[i])/last_long-1), f'{MA1} {MA2}')
                    profit_proc -= Decimal(df['Close'].iloc[i])/last_long-1
                    commission_proc -= commission*2
                    last_short = Decimal(df['Close'].iloc[i])
    return profit_proc, commission_proc


def check_profit_2_0(df, MA1, MA2):
    last_long = Decimal("0")
    last_short = Decimal("0")
    first = True
    commission = Decimal("0.00036") 
    commission_proc = Decimal("0")
    profit_proc = Decimal("0")
    
    price_poz_top_cp = get_price_poz_top_cp(df, 'MA1', 'MA2', MA2-1)
    

    for i in range(MA2-1, df.shape[0]-1):
        if price_poz_top_cp == False:
            if df['MA1'].iloc[i] > df['MA2'].iloc[i]:
                price_poz_top_cp = True
                write_to_file((Decimal(df['Close'].iloc[i])/last_short-1), f'{MA1} {MA2}')
                profit_proc += Decimal(df['Close'].iloc[i])/last_short-1
                commission_proc -= commission*2




    #print(price_poz_top_cp)
    for i in range(MA2-1, df.shape[0]-1):
        if price_poz_top_cp == False:
            if df['MA1'].iloc[i] > df['MA2'].iloc[i]:
                price_poz_top_cp = True
                if first == True:
                    last_long = Decimal(df['Close'].iloc[i])
                    first = False
                else:
                    # Продолжение лонга = знак -
                    write_to_file((Decimal(df['Close'].iloc[i])/last_short-1), f'{MA1} {MA2}')
                    profit_proc += Decimal(df['Close'].iloc[i])/last_short-1
                    commission_proc -= commission*2
                    last_long = Decimal(df['Close'].iloc[i])

                    
        elif price_poz_top_cp == True:
            if df['MA1'].iloc[i] < df['MA2'].iloc[i]:
                price_poz_top_cp = False
                if first == True:
                    last_short = Decimal(df['Close'].iloc[i])
                    first = False
                else:
                    # Продолжение лонга = знак +
                    write_to_file(-(Decimal(df['Close'].iloc[i])/last_long-1), f'{MA1} {MA2}')
                    profit_proc -= Decimal(df['Close'].iloc[i])/last_long-1
                    commission_proc -= commission*2
                    last_short = Decimal(df['Close'].iloc[i])
    return profit_proc, commission_proc

def profit_has_become_bigger(poz_top, poz_check, i, df):
    if poz_top == True:
        if poz_check < Decimal(df['Close'].iloc[i]):
            return True
    elif poz_top == False:
        if poz_check > Decimal(df['Close'].iloc[i]):
            return True

def check_profit_with_random(df):
    poz_main = Decimal("0")
    commission = Decimal("0.00036") 
    commission_proc = Decimal("0")
    profit_proc = Decimal("0")
    n = 5


    for i in range(1, df.shape[0]-1):

        if Decimal(df['Close'].iloc[i]) > Decimal(df['Close'].iloc[i-1]):
            poz_cur = True
        else:
            poz_cur = False
        # print(df['Close'].iloc[i])

        if poz_main == Decimal("0") and n >= 4:
            poz_main = Decimal(df['Close'].iloc[i]) 
            # print('точка входа\n')
        else:
            n += 1
            if poz_main != Decimal("0") and poz_cur is not poz_prev:
                if poz_cur is True:
                    profit_proc += Decimal(df['Close'].iloc[i])/poz_main-1
                    write_to_file((Decimal(df['Close'].iloc[i])/poz_main-1), str(coin))
                    # print('точка выхода')
                    # print('Прибыль ', -(Decimal(df['Close'].iloc[i])/poz_main-1), '\n')
                else:
                    profit_proc -= Decimal(df['Close'].iloc[i])/poz_main-1
                    write_to_file(-(Decimal(df['Close'].iloc[i])/poz_main-1), str(coin))
                    # print('точка выхода')
                    # print('Прибыль ', (Decimal(df['Close'].iloc[i])/poz_main-1), '\n')
                commission_proc -= commission*2
                poz_main = 0
                n = 0

        poz_prev = poz_cur
        
    return profit_proc, commission_proc

def check_profit_with_interval(df, MA1, MA2):
    poz_main = Decimal("0")
    commission = Decimal("0.00036") 
    commission_proc = Decimal("0")
    profit_proc = Decimal("0")
    poz_top_old = get_price_poz_top_cp(df, 'MA1', 'MA2', MA2-1)         # TEMP
    n = 0
    poz_check = Decimal("0")

    for i in range(MA2-1, df.shape[0]-1):
        if df['MA1'].iloc[i] > df['MA2'].iloc[i]:
            poz_top = True
        else:
            poz_top = False

        if poz_top != poz_top_old:
            poz_top_old = poz_top
            n = 0
            poz_check = Decimal(df['Close'].iloc[i])
            if poz_main != Decimal("0"):
                profit_proc -= Decimal(df['Close'].iloc[i])/poz_main-1
                write_to_file(-(Decimal(df['Close'].iloc[i])/poz_main-1), f'{MA1} {MA2}')
                commission_proc -= commission*2

                poz_main = 0
 
        if n >=  5 and poz_main == Decimal("0") and poz_check != Decimal("0") and profit_has_become_bigger(poz_top, poz_check, i, df):
            poz_main = Decimal(df['Close'].iloc[i]) 
            
        n+=1
    return profit_proc, commission_proc
        
def check_all_profit():
    for MA1 in range(2, 3):
        for MA2 in range(1, 20):
            MA2 *= 10

            average("MA1", MA1, df_full)
            average("MA2", MA2, df_full)
            # if os.path.exists('df_full_avg.csv'):
            #     os.remove('df_full_avg.csv')
            # df_full.to_csv('df_full_avg.csv')
            # df_full_avg = pd.read_csv('df_full_avg.csv')
            
            profit_proc, commission_proc = check_profit(df_full, MA1, MA2)

            print('Coin:', coin)
            print('MAs:', MA1, MA2)
            print('commission: ', round(commission_proc*100, 2), '%')
            print('profit: ', round((profit_proc)*100, 2), '%')
            print('clear profit: ', round((profit_proc + commission_proc)*100, 2), '%')
            print()
            
            # write_to_file(f'{(profit_proc + commission_proc)*100}', f'{MA1} {MA2}')
            
            # return (profit_proc + commission_proc)*100
            #print('profit: ', round(profit_point, 5), 'points')

if __name__ == '__main__':
    spinner = Spinner('Checking ')
    client = None
    while client == None:
        client = enter_api_key()
        
    listCoin = []
    coins = open('coins.txt')
    for row in coins: listCoin.append(row.rstrip())
    coins.close()

    # Settings
    coin = 'TRXUSDT'
    interval = '15m'
    limit = 1000
    length_MA1 = 1
    length_MA2 = 2
    length_MA3 = 80
    startTime = 1652572800
    # position_amount = get_position_amount()

    usdt_amount = 10        # in $

    df_full = pd.DataFrame(columns=['Opentime', 'Close', 'MA1', 'MA2'])
    
    ## Объявление DataFrame
    # df = pd.DataFrame()

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

    while int(round(time.time(), 0)) > startTime:
        df = get_history(startTime)
        df_full = pd.concat([df_full, df], ignore_index=True)
        startTime += 900000
    if os.path.exists('df_full.csv'):
        os.remove('df_full.csv')
    df_full.to_csv('df_full.csv')

    df_full = pd.read_csv('df_full.csv')
    print('История загружена\n')
    check_all_profit()

    # average("MA1", length_MA1, df_full)
    # average("MA2", length_MA2, df_full)
    # i = 0
    # while i < df.shape[0]-1:
    #     write_to_file(df_full['MA2'].iloc[i], 'check')
    #     i+=1
    # profit, commission = check_profit_with_3MA()
    # print('profit: ', round(profit*100, 2), '%')
    # print('commission: ', round(commission*100, 2), '%')
    # print('clear profit:', round((profit+commission) * 100, 2), '%')

    # Определение положения скользящих
    # price_poz_top = get_price_poz_top()
    # print(price_poz_top)

    # # Отображение графика
    # #buil_graf()
    # #plt.show(block=True)

    # # # Websocket
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
    #                     if df['MA1'].iloc[len(df.index)-2] > df['MA2'].iloc[len(df.index)-2]:
    #                         print('short')
    #                         #poz_short()
    #                         price_poz_top = True
    #                 elif price_poz_top == True:
    #                     if df['MA1'].iloc[len(df.index)-2] < df['MA2'].iloc[len(df.index)-2]:
    #                         print('long')
    #                         #poz_long()
    #                         price_poz_top = False
    #             #else:
    #                 # df.iloc[df.last_valid_index(), 0] = jsMessage['data']['k']['t']
    #                 # df.iloc[df.last_valid_index(), 1] = jsMessage['data']['k']['c']
    #                 # df["Close"] = df.Close.astype(float)

    #                 # average_last('MA1', length_MA1, df)
    #                 # average_last('MA2', length_MA2, df)
    #                 # buil_graf()

    #     else: 
    #         spinner.next()
    #         time.sleep(0.3)