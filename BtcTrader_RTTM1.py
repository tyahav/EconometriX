# *** Test Reversion to the Mean with BTC ***
import pandas as pd
import numpy as np
import requests
import io
import time
from datetime import datetime
import json

def getAssetPrice():
  while True:
    try:
      AVG_TIME = '1m'
      tnow = getServerTime()
      tpast =  tnow - 60 * 1000

      q = []
      q.append("symbol="+SYMBOL)
      q.append("interval="+AVG_TIME)
      q.append("startTime="+str(tpast))
      q.append("endTime="+str(tnow))
      data = '&'.join(q)

      response = requests.get(BASE+"/v3/klines",params=data)
      j = json.loads(response.content.decode("UTF-8"))
      
      prices = []
      for k in j:
        prices.append((float(k[1])+float(k[4]))/2)
      
      return prices[-1]
    except:
      time.sleep(1)
    
    

  #dataOK = False

  #while not dataOK:
  #  try:
  #    response = requests.get(BASE+"/v3/avgPrice",params="symbol="+SYMBOL)
  #    j = json.loads(response.content.decode("UTF-8"))
  #    p = float(j['price'])
  #    dataOK = True
  #  except:
  #    time.sleep(1)
  #
  #return p


def getLastValues(look_back_time_min):
  tnow = getServerTime()
  tpast =  tnow - look_back_time_min * 60 * 1000

  q = []
  q.append("symbol="+SYMBOL)
  q.append("interval=1m")
  q.append("startTime="+str(tpast))
  q.append("endTime="+str(tnow))
  data = '&'.join(q)

  response = requests.get(BASE+"/v3/klines",params=data)
  j = json.loads(response.content.decode("UTF-8"))
  
  prices = []
  for k in j:
    prices.append((float(k[1])+float(k[4]))/2)

  return prices

def getServerTime():
  response = requests.get(BASE+"/v3/time")
  j=json.loads(response.content.decode('UTF-8'))
  return int(j['serverTime'])

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


BASE = "https://api.binance.com/api"
SYMBOL = "BTCUSDT"

# Script Configuration
SLEEP_STEP_SEC = 1#60
SLEEP_POSITION_SEC = 5#60*5

# Trade parameters
LOOK_BACK_TIME_MIN = 60 * 1
DECREASE_BEF_BUY_STD = 1
INCREASE_BEF_SELL = 0.003
DECREASE_STOP_LOSS = 0.003

EWM_SMOOTH_SPAN = 10

profit = 1.0

buy_time = []
sell_prof_time = []
sell_loss_time = []
prev_values = []

print('starting...')

prev_values.extend(getLastValues(LOOK_BACK_TIME_MIN))

print('data collected, start trading...')


position = 'buy'

while True:
  
  current_val = getAssetPrice()  
  
  if position == 'buy':
	df_look_back_values = df_val[i-LOOK_BACK_TIME_MIN:i].ewm(span=10,adjust=False).mean() #smoothed
    mean_val = df_look_back_values.mean()
    std_val = df_look_back_values.std()

    if current_val < mean_val - DECREASE_BEF_BUY_STD * std_val:
      #time.sleep(SLEEP_POSITION_SEC)
      buy_time.append(datetime.now().time())
      buy_value = getAssetPrice()
      position = 'sell'
      print(datetime.now().time(), ' : buy value = ',buy_value)
  
  
  if position == 'sell':
    if current_val/buy_value-1 > INCREASE_BEF_SELL:
      #time.sleep(SLEEP_POSITION_SEC)
      next_val = getAssetPrice()
      profit *= next_val/buy_value
      sell_prof_time.append(datetime.now().time())
      position = 'buy'
      data_string = str(datetime.now().time()) + ' : sell value = ' + str(next_val) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
      writeData(data_string, profit)
    elif 1-current_val/buy_value > DECREASE_STOP_LOSS:
      #time.sleep(SLEEP_POSITION_SEC)
      next_val = getAssetPrice()
      profit *= next_val/buy_value
      sell_loss_time.append(datetime.now().time())
      position = 'buy'
      data_string = str(datetime.now().time()) + ' : sell value = ' + str(next_val) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
      writeData(data_string, profit)

  prev_values.append(current_val)
  time.sleep(SLEEP_STEP_SEC)