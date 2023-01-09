# Mean Reversion trade in Alpaca
# Version 19/05/21

import hashlib
import requests
import hmac
import datetime as dt
import time as tm
import time
import json
import alpaca_trade_api as tradeapi
import os
import numpy as np
import pandas as pd

# *** API Functions (Exchange Specific) ***

def getAssetPrice(ASSET):
  while True:
    try:
      time = '1'
      units = 'minute'
      barset = api.get_barset(ASSET,units, limit=time)
      assset_bars = barset[ASSET]
      
      return assset_bars[0].c #(assset_bars[0].o + assset_bars[0].c)/2
    except:
      tm.time.sleep(1)

def getServerTime():
  #response = requests.get(BASE+"/v3/time")
  #j=json.loads(response.content.decode('UTF-8'))
  #return int(j['serverTime'])
  #clock = api.get_clock()
  #clock.
  return

def getLastValues(ASSET, look_back_time_min):
  units = 'minute'
  barset = api.get_barset(ASSET, units, limit=look_back_time_min)
  assset_bars = barset[ASSET]
  
  prices = []
  for k in assset_bars:
    prices.append((k.o + k.c)/2)

  return prices

def writeData(data, profit):
  print(data)
  print('***profit = ',profit)
  f = open('log.txt', 'a') 
  f.write(data)
  f.close()
  
  g = open('trade.html', 'w')
  message = """<html>
  <head></head>
  <body><p>""" + str(dt.datetime.now().time()) + ' : ' + str(profit) + """</p></body>
  </html>""" 
  g.write(message)
  g.close()


def getCashInAccount():
  account = api.get_account()

  if account.trading_blocked:
      print('Account is currently restricted from trading.')
      return -1

  return float(account.cash)

def tradeBuyMarket(buy_amount):
  return 

def tradeBuyLimit(ASSET, quantity, buy_price):
  o = api.submit_order(
      symbol=ASSET,
      qty = quantity,
      side='buy',
      type='limit',
      limit_price = buy_price,
      time_in_force = 'gtc'
  )
  return o


def tradeSellMarket(sell_amount):
  return

def tradeSellLimit(ASSET, quantity, sell_price):
  o = api.submit_order(
      symbol=ASSET,
      qty = quantity,
      side='sell',
      type='limit',
      limit_price = sell_price,
      time_in_force = 'gtc'
  )
  return o

def getOrder(orderId):
  return api.get_order(orderId)

def cancelOrder(orderId):
  api.cancel_order(orderId)

def tradingDayTimeFraction():
  today_str = dt.date.today().strftime("%Y-%m-%d")
  cal = api.get_calendar(today_str, today_str)

  openTime = str(cal[0].open)
  closeTime = str(cal[0].close)
  curTime = str(clock.timestamp)[11:19]

  openTimeDT = time.strptime(openTime, "%H:%M:%S")
  closeTimeDT = time.strptime(closeTime, "%H:%M:%S")
  curTimeDT = time.strptime(curTime, "%H:%M:%S")

  t_open = time.mktime(openTimeDT)
  t_close = time.mktime(closeTimeDT)
  t_cur = time.mktime(curTimeDT)

  fraction = (t_cur - t_open) / (t_close - t_open)
  return fraction

# *** END OF API Functions ***

# *** TRADE LOGIC ***

# LOGIC PARAMETERS:
LOOK_BACK_TIME_MIN = 30
DECREASE_BEF_BUY_STD = 1
INCREASE_BEF_SELL = 0.003
DECREASE_STOP_LOSS = 0.003
EWM_SMOOTH_SPAN = 10

# LOGIC FUNCTIONS:

def preBuyLogic():
  for asset in ASSET_LIST:
    current_val = getAssetPrice(asset)
    look_back_values = np.array(pd.DataFrame(np.array(getLastValues(asset, LOOK_BACK_TIME_MIN))).ewm(span=EWM_SMOOTH_SPAN,adjust=False).mean())
    mean_val = look_back_values.mean()
    std_val = look_back_values.std()
    
    if current_val < mean_val - DECREASE_BEF_BUY_STD * std_val:
      return [asset,current_val]
  
  return ['NONE',0]
      
    
def postBuyLogic():
  return

def preSellLogic(buy_value):
  current_val = getAssetPrice(ASSET)
  if current_val/buy_value-1 > INCREASE_BEF_SELL or 1-current_val/buy_value > DECREASE_STOP_LOSS or tradingDayTimeFraction() > 8/9:
    return [True, current_val]
  else:
    return [False, -1]
    
def postSellLogic():
  return

# *** END OF TRADE LOGIC ***

# Account Config
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
APCA_API_KEY_ID = "PKEO4B0ACFWYQ01HM42F"
APCA_API_SECRET_KEY = "Y1gsBjZcPebz1buAMupLcTKjNNjE1FpoKP3O8t8o"

os.environ['APCA_API_BASE_URL'] = "https://paper-api.alpaca.markets"
os.environ['APCA_API_KEY_ID'] = "PKEO4B0ACFWYQ01HM42F"
os.environ['APCA_API_SECRET_KEY'] = "Y1gsBjZcPebz1buAMupLcTKjNNjE1FpoKP3O8t8o"

api = tradeapi.REST()

# Script Configuration
SLEEP_STEP_TRADE_SEC = 1
SLEEP_STEP_WAIT_SEC = 20*60

# Trade parameters
ASSET = 'NONE'

WAIT_ORDER_OPEN_MAX_ITER = 60

ACCOUNT_TRADE_RATIO = 0.1

profit = 1.0

ASSET_LIST = ['AAPL', 'MSFT','AMZN','GOOG','GOOGL', 'FB', 'TSLA','NVDA','PYPL']

print('starting...')

#prev_values.extend(getLastValues(LOOK_BACK_TIME_MIN))

print('')


position = 'wait'

while True:
  
  if position == 'buy':
    # check stats
    #look_back_values = np.array(pd.DataFrame(np.array(prev_values[-LOOK_BACK_TIME_MIN:])).ewm(span=EWM_SMOOTH_SPAN,adjust=False).mean())
    #if current_val/look_back_values.mean() - 1 > INCREASE_BEF_BUY:
    res = preBuyLogic()
    ASSET = res[0]
    buy_value = float(res[1])

    if ASSET != 'NONE':
      amount_to_buy = ACCOUNT_TRADE_RATIO * getCashInAccount()
      quantity = int(amount_to_buy/buy_value)
      order = tradeBuyLimit(ASSET, quantity, buy_value)
      print(order)
      wait_order_count=0
      position = 'pending_buy'

  if position == 'pending_buy':
      wait_order_count = wait_order_count + 1    
      lastBuyOrder = getOrder(order.id)
      print(lastBuyOrder.status)
      if lastBuyOrder.status == "filled" or lastBuyOrder.status == "partially_filled":
        buy_qty = float(lastBuyOrder.filled_qty)
        buy_value = float(lastBuyOrder.filled_avg_price)
        data_string = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : buy value = ' + str(buy_value) + ' buy qty = ' + str(buy_qty)
        writeData(data_string, profit)        
        postBuyLogic()
        position = 'sell'
      if lastBuyOrder.status == "canceled" or lastBuyOrder.status == "expired":
        position = 'buy'
      if lastBuyOrder.status == "new" and wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        print('cancel buy order id: ', lastBuyOrder.id)
        cancelOrder(lastBuyOrder.id)
        position = 'pending_buy'

  if position == 'sell':
    res = preSellLogic(buy_value)
    if bool(res[0]):
      sell_value = float(res[1])
      order = tradeSellLimit(ASSET, buy_qty, sell_value)
      lastSellOrderID = order.id
      #sell_value = float(res[1])
      wait_order_count=0
      print(order)
      position = 'pending_sell'
  
  if position == 'pending_sell':
      wait_order_count = wait_order_count + 1    
      lastSellOrder = getOrder(lastSellOrderID)
      if lastSellOrder.filled_at != None:
        sell_tot_qty = float(lastSellOrder.qty)
        sell_qty = float(lastSellOrder.filled_qty)
        sell_value = float(lastSellOrder.filled_avg_price)
        profit *= sell_value/buy_value
        print(profit)
        data_string = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : sell value = ' + str(sell_value) + ' sell qty = ' + str(sell_qty) + '\n' + str(dt.datetime.now().time()) + ' : *** profit = ' + str(profit)
        writeData(data_string, profit)
        if sell_qty == sell_tot_qty:
          postSellLogic()
          position = 'buy'
        if sell_qty > 0 and sell_qty < sell_tot_qty:
          buy_qty -= sell_qty
          position = 'sell'
      if lastBuyOrder.expired_at != None or lastBuyOrder.canceled_at != None or lastBuyOrder.failed_at != None:
        position = 'sell'
      if wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        cancelOrder(lastSellOrderID)
        print('order canceled: ',lastSellOrderID)
        position = 'sell'

  if position == 'wait':
    clock = api.get_clock()
    if clock.is_open:
      SLEEP_STEP_SEC = SLEEP_STEP_TRADE_SEC 
      if tradingDayTimeFraction() > 1/9:
        position = 'buy'
    else:
      print('waiting for markets...')
      SLEEP_STEP_SEC = SLEEP_STEP_WAIT_SEC

  
  time.sleep(SLEEP_STEP_SEC)
