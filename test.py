# from binance.spot import Spot as SpotClient
# from binance.client import Client
# from binance.enums import *
# import time
# import datetime
# import json
# from threading import Thread
# import math
# from decimal import Decimal

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

# coin = 'DOGEUSDT'
# client = Client(
# api_key = '9YFuTICk3DzXd7PYVyJA9BgOXM1ktEjfIbEhVZoy2FcgNwbdi2V0zzAzYPJ4DbkO', 
# api_secret = 'xLkCdvdWvwQ2ZMKNQTZwz1HjKEUGq2VtFfO0nhWRmzsRARbixO1jmszFDXvuvOGi')

# order = client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=60)
# print(order)
# FuturesStopLoss =client.futures_create_order(
#    symbol=coin,
#    type='STOP_MARKET',
#    side='SELL',
#    stopPrice=0.129691,
#    closePosition=True
#    )

# def close_unprofitable_positions():
#     try:
#         x = client.futures_account()['positions']
#         for i in x:
#             if i['symbol'] == coin and i['positionAmt'] != '0' and float(i['unrealizedProfit']) < -stop_loss:
#                 if float(i['positionAmt']) > 0:
#                     order = client.futures_create_order(symbol=coin, side='SELL', type='MARKET', quantity=abs(float(i['positionAmt'])))
#                     print(f"SELL: {order}")
#                 elif float(i['positionAmt']) < 0:
#                     order = client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=abs(float(i['positionAmt'])))
#                     print(f"BUY: {order}")
#     except Exception as e:
#         print(e)
#         time.sleep(5)
#         close_unprofitable_positions()

# def get_position_amount():
#     try:
#         balance = client.futures_account_balance()
#         for i in balance:
#             if i['asset'] == 'USDT':
#                 # trading_amount = float(i['balance']) * trading_ratio
#                 trading_amount = 10
#         coin_price = client.get_symbol_ticker(symbol = coin)
#         return round(trading_amount/float(coin_price['price']))
#     except Exception as e:
#         print(e)
#         time.sleep(5)
#         get_position_amount()

# info = client.futures_exchange_info()
# for x in info['symbols']:
#     f.write(x['symbol'] +': '+ str(x['pricePrecision']) + "\n")


# x = client.futures_account()
# for i in x:
#     f.write("\n" + str(i))//////////


# balance = client.futures_account_balance()
# for i in balance:
#     if i['asset'] == 'USDT':
#         trade_balance = float(i['balance']) * 0.1
#         print(trade_balance)

mama = False
papa = True

if mama is not papa:
    print('True')
else:
    print('False')
