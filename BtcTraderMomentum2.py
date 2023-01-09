import pandas as pd
import numpy as np
import requests
import io
import time
from datetime import datetime

def getBitcoinPrice():
  dataOK = False
  while not dataOK:
    try:
      bit_data = pd.read_json("https://blockchain.info/ticker")
      dataOK = True
    except:
      time.sleep(1)

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
INCREASE_BEF_BUY = ARB
INCREASE_BEF_SELL = ARB
DECREASE_STOP_LOSS = ARB

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
	# ADD : smoothing with ewm span = 10
	# df_val[i-LOOK_BACK_TIME_MIN:i].ewm(span=10,adjust=False).mean()
    look_back_values = np.array(prev_values[-LOOK_BACK_TIME_MIN:])
    slope = np.diff(look_back_values).mean()

    if current_val/look_back_values.mean() - 1 > INCREASE_BEF_BUY:
      time.sleep(SLEEP_POSITION_SEC)
      buy_time.append(datetime.now().time())
      buy_value = getBitcoinPrice()
      position = 'sell'
      print(datetime.now().time(), ' : buy value = ',buy_value)
  
  
  if position == 'sell':
    if current_val/buy_value-1 > INCREASE_BEF_SELL:
      time.sleep(SLEEP_POSITION_SEC)
      next_val = getBitcoinPrice()
      profit *= next_val/buy_value
      sell_prof_time.append(datetime.now().time())
      position = 'buy'
      data_string = str(datetime.now().time()) + ' : sell value = ' + str(next_val) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
      writeData(data_string, profit)
    elif 1-current_val/buy_value > DECREASE_STOP_LOSS:
      time.sleep(SLEEP_POSITION_SEC)
      next_val = getBitcoinPrice()
      profit *= next_val/buy_value
      sell_loss_time.append(datetime.now().time())
      position = 'buy'
      data_string = str(datetime.now().time()) + ' : sell value = ' + str(next_val) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
      writeData(data_string, profit)

  prev_values.append(current_val)
  time.sleep(SLEEP_STEP_SEC)