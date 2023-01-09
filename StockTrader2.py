# Mean Reversion trade in Alpaca
# HFT Version
# Version 12/06/21

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
  if ASSET == 'NONE':
    print('NONE has no price')
    return -1

  while True:
    try:
      #print('retrieve ',ASSET)
      time = '1'
      units = 'minute'
      barset = api.get_barset(ASSET,units, limit=time)
      assset_bars = barset[ASSET]
      
      return assset_bars[0].c #(assset_bars[0].o + assset_bars[0].c)/2
    except:
      print('FAILED retrieving price for',ASSET)
      tm.time.sleep(3)

def getAssetBar(ASSET):
  if ASSET == 'NONE':
    print('NONE has no price')
    return -1

  while True:
    try:
      #print('retrieve ',ASSET)
      time = '1'
      units = 'minute'
      barset = api.get_barset(ASSET,units, limit=time)
      assset_bars = barset[ASSET]
      
      return assset_bars[0] #(assset_bars[0].o + assset_bars[0].c)/2
    except:
      print('FAILED retrieving price for',ASSET)
      tm.time.sleep(3)

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


def tradeSellMarket(ASSET, quantity):
  o = api.submit_order(
      symbol=ASSET,
      qty = quantity,
      side='sell',
      type='market',
      time_in_force = 'gtc'
  )
  return o

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
PROFIT_SELL_TRY_COUNT = 3
profit_sell_try_count = PROFIT_SELL_TRY_COUNT
SELL_PRICE_FACTOR = 1

# LOGIC FUNCTIONS:

def preBuyLogic():
  best_asset = 'NONE'
  best_value = 0
  best_ratio = 0
  for asset in ASSET_LIST:
    print('check ', asset)
    current_val = getAssetPrice(asset)
    current_bar = getAssetBar(asset)
    ratio = (current_bar.h - current_bar.c) / (current_bar.h - current_bar.l)
    

    if current_val < mean_val - DECREASE_BEF_BUY_STD * std_val:
      if ratio > best_ratio:
        #best_ratio = std_val/mean_val
        #best_asset = asset
        best_value = current_val
        best_ratio = ratio
        best_asset = asset
  
  return [best_asset,best_value]
      
    
def postBuyLogic():
  return

def preSellLogic(buy_value, count):
  current_val = getAssetPrice(ASSET)
  current_bar = getAssetBar(ASSET)
  sell_price = current_bar.h
  if profit_sell_try_count > 0 or tradingDayTimeFraction() > 0.95:
    profit_sell_try_count=-1
    return ['limit' , sell_price]
  else:
    return ['market', -1]
    
def postSellLogic():
  profit_sell_try_count = PROFIT_SELL_TRY_COUNT

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

WAIT_ORDER_OPEN_MAX_ITER = 3

ACCOUNT_TRADE_RATIO = 0.1

profit = 1.0
success_count = 0
trade_count = 0

ASSET_LIST = ['AAPL', 'MSFT','AMZN','GOOG','GOOGL', 'FB', 'TSLA','NVDA','PYPL','NFLX','ADBE','AVGO','COST','SNPS','TXN','PEP','SBUX','AEP','MRVL']

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
      if quantity > 0:
        try:
          order = tradeBuyLimit(ASSET, quantity, buy_value)
          print(order)
          wait_order_count=0
          position = 'pending_buy'
        except:
          position = 'buy'

  if position == 'pending_buy':
      wait_order_count = wait_order_count + 1    
      lastBuyOrder = getOrder(order.id)
      print(lastBuyOrder.status)
      if lastBuyOrder.status == "filled" or lastBuyOrder.status == "partially_filled":
        buy_qty = float(lastBuyOrder.filled_qty)
        buy_value = float(lastBuyOrder.filled_avg_price)
        data_string = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : stock = '+ ASSET +' buy value = ' + str(buy_value) + ' buy qty = ' + str(buy_qty)
        writeData(data_string, profit)
        print('profit = {0:.3f}   success rate = {1:.3f}]'.format(profit, success_count/trade_count))        
        postBuyLogic()
        position = 'sell'
        trade_count += 1
      if lastBuyOrder.status == "canceled" or lastBuyOrder.status == "expired":
        position = 'buy'
      if lastBuyOrder.status == "new" and wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        print('cancel buy order id: ', lastBuyOrder.id)
        cancelOrder(lastBuyOrder.id)
        position = 'pending_buy'

  if position == 'sell':
    res = preSellLogic(buy_value)
    if res[0] == 'limit':
      sell_value = float(res[1])
      order = tradeSellLimit(ASSET, buy_qty, sell_value)
    else:
      sell_value = float(res[1])
      order = tradeSellMarket(ASSET, buy_qty)
    lastSellOrderID = order.id
    #sell_value = float(res[1])
    wait_order_count=0
    print(order)
    position = 'pending_sell'
  
  if position == 'pending_sell':
      wait_order_count = wait_order_count + 1    
      lastSellOrder = getOrder(lastSellOrderID)
      if lastSellOrder.status == "filled" or lastSellOrder.status == "partially_filled":
        sell_tot_qty = float(lastSellOrder.qty)
        sell_qty = float(lastSellOrder.filled_qty)
        sell_value = float(lastSellOrder.filled_avg_price)
        profit *= sell_value/buy_value
        if sell_value/buy_value > 1:
          success_count +=1

        data_string = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : stock = ' + ASSET + ' sell value = ' + str(sell_value) + ' sell qty = ' + str(sell_qty) + '\n' + str(dt.datetime.now().time()) + ' : *** profit = ' + str(profit)
        writeData(data_string, profit)
        print('profit = {0:.3f}   success rate = {1:.3f}]'.format(profit, success_count/trade_count))
        if sell_qty == sell_tot_qty:
          postSellLogic()
          ASSET = 'NONE'
          position = 'wait'
        if sell_qty > 0 and sell_qty < sell_tot_qty:
          buy_qty -= sell_qty
          position = 'sell'
      if lastSellOrder.status == 'expired' or lastSellOrder.status == 'failed' or lastSellOrder.status == 'canceled':
        position = 'sell'
      if wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        cancelOrder(lastSellOrderID)
        print('order canceled: ',lastSellOrderID)
        position = 'sell'

  if position == 'wait':
    clock = api.get_clock()
    if clock.is_open:
      SLEEP_STEP_SEC = SLEEP_STEP_TRADE_SEC 
      f = tradingDayTimeFraction()
      if f > 0.05 and f < 0.95:
        position = 'buy'
    else:
      print('waiting for markets...')
      SLEEP_STEP_SEC = SLEEP_STEP_WAIT_SEC

  
  time.sleep(SLEEP_STEP_SEC)
