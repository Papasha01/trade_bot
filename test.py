from binance.spot import Spot as SpotClient
from binance.client import Client
from binance.enums import *
import time
import datetime
import json
from threading import Thread
import math
from decimal import Decimal

# x = 5.41
# a = Decimal("5")
# b = Decimal(float(56.4))
# c = Decimal(3)

# c += 2
# print(a+b+c)

# print(float(D(0.1**1).quantize(D("1.000000"))))
# print(float(D(0.1**2).quantize(D("1.000000"))))
# print(float(D(0.1**3).quantize(D("1.000000"))))
# print(float(D(0.1**4).quantize(D("1.000000"))))
# print(float(D(0.1**5).quantize(D("1.000000"))))
# print(float(D(0.1**6).quantize(D("1.000000"))))

# f = open('Coin_pricePrecision.txt', 'w+')

coin = 'DOGEUSDT'
client = Client(
api_key = '9YFuTICk3DzXd7PYVyJA9BgOXM1ktEjfIbEhVZoy2FcgNwbdi2V0zzAzYPJ4DbkO', 
api_secret = 'xLkCdvdWvwQ2ZMKNQTZwz1HjKEUGq2VtFfO0nhWRmzsRARbixO1jmszFDXvuvOGi')

# order = client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=60)
# print(order)
# FuturesStopLoss =client.futures_create_order(
#    symbol=coin,
#    type='STOP_MARKET',
#    side='SELL',
#    stopPrice=0.129691,
#    closePosition=True
#    )

# info = client.futures_exchange_info()
# for x in info['symbols']:
#     f.write(x['symbol'] +': '+ str(x['pricePrecision']) + "\n")


# x = client.futures_account()
# for i in x:
#     f.write("\n" + str(i))//////////


balance = client.futures_account_balance()
for i in balance:
    if i['asset'] == 'USDT':
        trade_balance = float(i['balance']) * 0.1
        print(trade_balance)
