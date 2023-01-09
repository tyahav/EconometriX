import pandas as pd
import numpy as np
import requests
import io
import time
from datetime import datetime

def getBitcoinPrice():
  bit_data = pd.read_json("https://blockchain.info/ticker")
  return bit_data['USD']['last']

def writeData(data, profit):
  print(data)
  f = open('log.txt', 'a') 
  f.write(data)
  f.close()
  
  g = open('trade.html', 'w')
  message = """<html>
  <head></head>
  <body><p>""" + str(datetime.now().time()) + ' : ' + str(profit) + """</p></body>
  </html>""" 
  g.write(message)
  g.close()


# Script Configuration
SLEEP_STEP_SEC = 60
SLEEP_POSITION_SEC = 60*5

# Trade parameters
ARB = 0.01
LOOK_BACK_TIME_MIN = 60 * 1
DROP_TO_BUY =  2 * ARB
DROP_TO_SELL = 1 * ARB
PRICE_COUNT_LIMIT_BUY = 10
BUY_PROFIT_EXP = 1.0
SELL_PROFIT_EXP = -0.01
PRICE_COUNT_LIMIT_BUY_MAX = 50
PRICE_COUNT_LIMIT_BUY_MINMAX = 15

profit = 1.0

buy_time = []
sell_prof_time = []
sell_loss_time = []
prev_values = []

print('starting...')

while len(prev_values) <= LOOK_BACK_TIME_MIN:
  prev_values.append(getBitcoinPrice())
  time.sleep(SLEEP_STEP_SEC)
print('data collected, start trading...')


position = 'buy'

while True:
  
  current_val = getBitcoinPrice()  
  
  if position == 'buy':
    # check stats
    a = np.array(prev_values[-1*LOOK_BACK_TIME_MIN:])
    cnt = len(a[current_val > (1+ARB)*a])

    if cnt > max(PRICE_COUNT_LIMIT_BUY, min(PRICE_COUNT_LIMIT_BUY_MINMAX,PRICE_COUNT_LIMIT_BUY*(profit**(BUY_PROFIT_EXP)))) and cnt < PRICE_COUNT_LIMIT_BUY_MAX:
      time.sleep(SLEEP_POSITION_SEC)
      buy_time.append(datetime.now().time())
      buy_value = getBitcoinPrice()
      position = 'sell'
      print(datetime.now().time(), ' : buy value = ',buy_value)
  
  if position == 'sell':
    if current_val/buy_value-1 > ARB:
      time.sleep(SLEEP_POSITION_SEC)
      next_val = getBitcoinPrice()
      profit *= next_val/buy_value
      sell_prof_time.append(datetime.now().time())
      position = 'buy'
      data_string = str(datetime.now().time()) + ' : sell value = ' + str(next_val) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
      writeData(data_string, profit)
    elif 1-current_val/buy_value > min(DROP_TO_SELL, (profit**(SELL_PROFIT_EXP))*DROP_TO_SELL):
      time.sleep(SLEEP_POSITION_SEC)
      next_val = getBitcoinPrice()
      profit *= next_val/buy_value
      sell_loss_time.append(datetime.now().time())
      position = 'buy'
      data_string = str(datetime.now().time()) + ' : sell value = ' + str(next_val) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
      writeData(data_string, profit)

  prev_values.append(current_val)
  time.sleep(SLEEP_STEP_SEC)