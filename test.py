from binance.spot import Spot as SpotClient
from binance.client import Client
from binance.enums import *
import time
import datetime
import json
from threading import Thread

f = open('python-binance.txt', 'w+')

coin = 'DOGEUSDT'
client = Client(
api_key = '9YFuTICk3DzXd7PYVyJA9BgOXM1ktEjfIbEhVZoy2FcgNwbdi2V0zzAzYPJ4DbkO', 
api_secret = 'xLkCdvdWvwQ2ZMKNQTZwz1HjKEUGq2VtFfO0nhWRmzsRARbixO1jmszFDXvuvOGi')

order = client.futures_create_order(symbol=coin, side='BUY', type='MARKET', quantity=60)
x = client.futures_account()['positions']
for i in x:
    if float(i['positionAmt']) > 0:
        f.write("\n" + str(i))