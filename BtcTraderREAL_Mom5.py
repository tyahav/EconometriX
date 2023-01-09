# Momentum trade in binance
# Version 13/03/21

import requests
import hashlib
import hmac
import pandas as pd
import numpy as np
import requests
import io
import time
import datetime as dt
from datetime import datetime
import json

# *** API Functions (Exchange Specific) ***

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

def getServerTime():
  response = requests.get(BASE+"/v3/time")
  j=json.loads(response.content.decode('UTF-8'))
  return int(j['serverTime'])

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


def writeData(data, profit):
  print(data)
  print('***profit = ',profit)
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

def getAmountInAccount(asset):
  tss = str(int(time.time()*1000))
  data = "timestamp="+ tss
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.get(BASE+"/v3/account",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))

  for b in j['balances']:
    if b['asset']==asset:
      return float(b['free'])
  
  return -1

def tradeBuyMarket(buy_amount):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=BUY")
  q.append("type=MARKET")
  q.append("quoteOrderQty="+"{:.2f}".format(buy_amount))
  q.append("timestamp="+ tss)

  data = '&'.join(q)
  bdata= data.encode('utf-8')

  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  return j

def tradeBuyLimit(buy_amount, buy_price):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=BUY")
  q.append("type=LIMIT")
  q.append("timeInForce=GTC")
  q.append("quantity="+"{:.6f}".format(int((buy_amount/buy_price)*1000000)/1000000))
  q.append("price="+"{:.2f}".format(int(buy_price*100)/100))
  q.append("timestamp="+ tss)

  data = '&'.join(q)
  bdata= data.encode('utf-8')
  print(data)
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  print(j)
  return j


def tradeSellMarket(sell_amount):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=SELL")
  q.append("type=MARKET")
  q.append("quantity="+"{:.2f}".format(sell_amount))
  q.append("timestamp="+ tss)
  data = '&'.join(q)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  return j

def tradeSellLimit(base_qty, sell_price):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=SELL")
  q.append("type=LIMIT")
  q.append("timeInForce=GTC")
  q.append("quantity="+"{:.6f}".format(int(base_qty*1000000)/1000000))
  q.append("price="+"{:.2f}".format(int(sell_price*100)/100))
  q.append("timestamp="+ tss)
  data = '&'.join(q)
  print(data)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  print(j)
  return j

def getOrder(orderId):
  ordType = "allOrders" #"allOrders" #"openOrders"
  tss = str(int(time.time()*1000))
  q = []
  q.append("timestamp="+ tss)
  q.append("symbol="+SYMBOL)
  data = '&'.join(q)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.get(BASE+"/v3/"+ordType,params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  for ord in j:
    if ord['orderId'] == orderId:
      return ord
  
  return {'status' : 'NA'}

def cancelOrder(orderId):
  tss = str(int(time.time()*1000))
  q = []
  q.append("timestamp="+ tss)
  q.append("symbol="+SYMBOL)
  q.append("orderId="+str(orderId))
  data = '&'.join(q)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.delete(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  print(j)
  return j

def getSymbolFilters(symbol):
  response = requests.get(BASE+"/v3/exchangeInfo",headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  for sym in j['symbols']:
    if sym['symbol'] == symbol:
      return sym['filters']

def getFilterValue(symbol, filter):
  j=getSymbolFilters(symbol)
  for f in j:
    if f['filterType'] == filter:
      return f

# *** END OF API Functions ***

# *** TRADE LOGIC ***

# LOGIC PARAMETERS:
LOOK_BACK_TIME_MIN = 30
INCREASE_BEF_BUY = 0.003
INCREASE_BEF_SELL = 0.005
DECREASE_STOP_LOSS = 0.005
EWM_SMOOTH_SPAN = 5

SLEEP_AFTER_BUY_MIN = 15
# LOGIC FUNCTIONS:

def preBuyLogic(current_val):
  look_back_values = np.array(pd.DataFrame(np.array(getLastValues(LOOK_BACK_TIME_MIN))).ewm(span=EWM_SMOOTH_SPAN,adjust=False).mean())
  if current_val/look_back_values.min() - 1 > INCREASE_BEF_BUY:
    return True
  else:
    return False
    
def postBuyLogic():
  return

def preSellLogic(buy_value, current_val):
  if current_val/buy_value-1 > INCREASE_BEF_SELL or 1-current_val/buy_value > DECREASE_STOP_LOSS:
    return True
  else:
    return False
    
def postSellLogic():
  time.sleep(SLEEP_AFTER_BUY_MIN * 60)
  return

# *** END OF TRADE LOGIC ***

# Account Config
HEAD = {'X-MBX-APIKEY' : 'CnUpsTP64PnycrnhjWqGDWoFyfqpsr8AKQekh1375Frb1Ioq6Af8cDWoGONVsYXG'}
KEY = '1NzXSpWjrvcy4n89POPufNfT9fz6YnxBjxrSnWKkROLgKPYFem7qiQJzLsnlmcnA'
bkey = KEY.encode('utf-8')
	  
# Script Configuration
BASE = "https://api.binance.com/api"
SLEEP_STEP_SEC = 1

# Trade parameters
SYMBOL = "BTCUSDT"

BASE_ASSET='BTC'
QUOTE_ASSET='USDT'

WAIT_ORDER_OPEN_MAX_ITER = 10

ACCOUNT_TRADE_RATIO = 1

profit = 1.0


prev_values = []

print('starting...')

prev_values.extend(getLastValues(LOOK_BACK_TIME_MIN))

print('')
print('data collected, start trading...')


position = 'buy'

while True:
  
  current_val = getAssetPrice()  
  if position == 'buy':
    # check stats
    #look_back_values = np.array(pd.DataFrame(np.array(prev_values[-LOOK_BACK_TIME_MIN:])).ewm(span=EWM_SMOOTH_SPAN,adjust=False).mean())
    #if current_val/look_back_values.mean() - 1 > INCREASE_BEF_BUY:

    if preBuyLogic(current_val):
      amount_to_buy = ACCOUNT_TRADE_RATIO*getAmountInAccount(QUOTE_ASSET)
      print(amount_to_buy, current_val)
      j = tradeBuyLimit(amount_to_buy, current_val)

      #qty_base_comm_total = 0
      #for f in j['fills']:
      #  qty_base_comm_total += float(f['commission'])
	  
      lastBuyOrderID = int(j['orderId'])
      buy_value = current_val

      wait_order_count=0
      position = 'pending_buy'

  if position == 'pending_buy':
      wait_order_count = wait_order_count + 1    
      lastBuyOrder = getOrder(lastBuyOrderID)
      #print(lastBuyOrder)
      if lastBuyOrder['status'] == 'FILLED' or lastBuyOrder['status'] == 'PARTIALLY_FILLED':
        buy_amount = float(lastBuyOrder['cummulativeQuoteQty'])
        buy_base_qty = 0.999*float(lastBuyOrder['executedQty']) #- qty_base_comm_total
        data_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : buy value = ' + str(buy_value) + ' buy amount = ' + str(buy_amount)
        writeData(data_string, profit)        
        amount_to_sell = buy_amount

        postBuyLogic()
        position = 'sell'
      if lastBuyOrder['status'] == 'REJECTED' or lastBuyOrder['status'] == 'EXPIRED' or lastBuyOrder['status'] == 'CANCELED':
        position = 'buy'
      if wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        print('cancel buy order id: ', lastBuyOrderID)
        cancelOrder(lastBuyOrderID)
        position = 'pending_buy'

  if position == 'sell':
    if preSellLogic(buy_value, current_val):
      #amount_to_sell = getAmountInAccount(BASE_ASSET)
      #max_sell_value_allowed = float(getFilterValue(SYMBOL,'MARKET_LOT_SIZE')['maxQty'])
      #print('max lot: ',max_sell_value_allowed)
      #if (amount_to_sell > max_sell_value_allowed):
      #  amount_to_sell = max_sell_value_allowed

      j = tradeSellLimit(buy_base_qty, current_val)
      lastSellOrderID = int(j['orderId'])
      sell_value = current_val
      wait_order_count=0
      position = 'pending_sell'
  
  if position == 'pending_sell':
      wait_order_count = wait_order_count + 1    
      lastSellOrder = getOrder(lastSellOrderID)
      if lastSellOrder['status'] == 'FILLED' or lastSellOrder['status'] == 'PARTIALLY_FILLED':
        sell_amount = float(lastSellOrder['cummulativeQuoteQty'])
        profit *= sell_amount/buy_amount
        print(profit)
        data_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : sell value = ' + str(sell_value) + ' sell amount = ' + str(sell_amount) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
        writeData(data_string, profit)
        if lastSellOrder['status'] == 'FILLED':
          wait_count_sec = 30*60
          postSellLogic()
          position = 'buy'
        if lastSellOrder['status'] == 'PARTIALLY_FILLED':
          buy_base_qty -= float(lastBuyOrder['executedQty'])
          position = 'sell'
      if lastSellOrder['status'] == 'REJECTED' or lastSellOrder['status'] == 'EXPIRED' or lastSellOrder['status'] == 'CANCELED':
        position = 'sell'
      if wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        #cancelOrder(lastSellOrderID)
        print('order canceled: ',lastSellOrderID)
        #position = 'sell'

  if position == 'wait':
      if wait_count_sec > 0:
        wait_count_sec -= 1
      else:
        position = 'buy'

  #prev_values.append(current_val)
  time.sleep(SLEEP_STEP_SEC)
