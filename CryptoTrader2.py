# Crypto Trader (Binance)
# Version 15/06/21

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

def getAssetPrice(asset):
  dataOK = False
  while not dataOK:
    try:
      response = requests.get(BASE+"/v3/avgPrice",params="symbol="+asset)
      j = json.loads(response.content.decode("UTF-8"))
      p = float(j['price'])
      dataOK = True
    except:
      time.sleep(1)

  return p

def getServerTime():
  response = requests.get(BASE+"/v3/time")
  j=json.loads(response.content.decode('UTF-8'))
  return int(j['serverTime'])

def getLastValues(asset,look_back_time_min):
  tnow = getServerTime()
  tpast =  tnow - look_back_time_min * 60 * 1000

  q = []
  q.append("symbol="+asset)
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

def tradeBuyMarket(asset,buy_amount):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+asset)
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

def tradeBuyLimit(asset,qty,buy_price):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+asset)
  q.append("side=BUY")
  q.append("type=LIMIT")
  q.append("timeInForce=GTC")
  q.append("quantity="+str(qty)) #"{:.6f}".format(int((buy_amount/buy_price)*1000000)/1000000))
  q.append("price="+str(buy_price)) #"{:.2f}".format(int(buy_price*100)/100))
  q.append("timestamp="+ tss)

  data = '&'.join(q)
  bdata= data.encode('utf-8')
  print(data)
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  print(j)
  return j


def tradeSellMarket(asset,sell_amount):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+asset)
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

def tradeSellLimit(asset,base_qty, sell_price):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+asset)
  q.append("side=SELL")
  q.append("type=LIMIT")
  q.append("timeInForce=GTC")
  q.append("quantity="+str(base_qty)) #"{:.8f}".format(int(base_qty*100000000)/100000000))
  q.append("price="+str(sell_price)) #"{:.2f}".format(int(sell_price*100)/100))
  q.append("timestamp="+ tss)
  data = '&'.join(q)
  print(data)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  print(j)
  return j

def getOrder(asset,orderId):
  ordType = "allOrders" #"allOrders" #"openOrders"
  tss = str(int(time.time()*1000))
  q = []
  q.append("timestamp="+ tss)
  q.append("symbol="+asset)
  data = '&'.join(q)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.get(BASE+"/v3/"+ordType,params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  for ord in j:
    if ord['orderId'] == orderId:
      return ord
  
  return {'status' : 'NA'}

def cancelOrder(asset,orderId):
  tss = str(int(time.time()*1000))
  q = []
  q.append("timestamp="+ tss)
  q.append("symbol="+asset)
  q.append("orderId="+str(orderId))
  data = '&'.join(q)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.delete(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  print(j)
  return j

def getSymbolFilters(asset):
  response = requests.get(BASE+"/v3/exchangeInfo",headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  for sym in j['symbols']:
    if sym['symbol'] == asset:
      return sym['filters']

def getFilterValue(asset, filter):
  j=getSymbolFilters(asset)
  for f in j:
    if f['filterType'] == filter:
      return f

def formatQuantity(asset, qty):
  filter = getFilterValue(asset,'LOT_SIZE')
  l = filter['stepSize'].index('1') - 1
  return float(str('{:.'+str(l)+'f}').format(qty))

  return int(qty * qf) / qf

def formatPrice(asset, price):
  filter = getFilterValue(asset,'PRICE_FILTER')
  l = filter['tickSize'].index('1') - 1
  return float(str('{:.'+str(l)+'f}').format(price))

# *** TRADE LOGIC ***

# LOGIC PARAMETERS:
LOOK_BACK_TIME_MIN = 12 * 60
DECREASE_BEF_BUY_STD = 1
INCREASE_BEF_SELL = 0.02
DECREASE_STOP_LOSS = 0.15
EWM_SMOOTH_SPAN = 10

def preBuyLogic():
  best_asset = 'NONE'
  best_value = 0
  best_ratio = 0
  for base_asset in BASE_ASSET_LIST:
    asset = base_asset + QUOTE_ASSET
    print('check ', asset)
    current_val = getAssetPrice(asset)
    look_back_values = np.array(pd.DataFrame(np.array(getLastValues(asset, LOOK_BACK_TIME_MIN))).ewm(span=EWM_SMOOTH_SPAN,adjust=False).mean())
    mean_val = look_back_values.mean()
    std_val = look_back_values.std()
    ratio = std_val/mean_val
    
    if current_val < mean_val - DECREASE_BEF_BUY_STD * std_val:
      print('buy condition = true')
      if ratio > best_ratio:
        best_value = current_val
        best_ratio = ratio
        best_asset = asset
  print([best_asset,best_value])
  return [best_asset,best_value]
      
    
def postBuyLogic():
  return

def preSellLogic(buy_value):
  current_val = getAssetPrice(ASSET)
  if current_val/buy_value-1 > INCREASE_BEF_SELL or 1-current_val/buy_value > DECREASE_STOP_LOSS:
    return [True, current_val]
  else:
    return [False, -1]



# Account Config
HEAD = {'X-MBX-APIKEY' : 'CnUpsTP64PnycrnhjWqGDWoFyfqpsr8AKQekh1375Frb1Ioq6Af8cDWoGONVsYXG'}
KEY = '1NzXSpWjrvcy4n89POPufNfT9fz6YnxBjxrSnWKkROLgKPYFem7qiQJzLsnlmcnA'
bkey = KEY.encode('utf-8')
	  
# Script Configuration
BASE = "https://api.binance.com/api"
SLEEP_STEP_SEC = 1

# Trade parameters
ASSET = 'NONE'
BASE_ASSET_LIST = ['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'BCH', 'LTC']
QUOTE_ASSET='USDT'


WAIT_ORDER_OPEN_MAX_ITER = 5
ACCOUNT_TRADE_RATIO = 0.9
FEE = 0.999

profit = 1.0
success_count = 0
trade_count = 0

print('start trading...')

position = 'buy'

while True:
  
  if position == 'buy':
    res = preBuyLogic()
    ASSET = res[0]
    buy_value = formatPrice(ASSET,float(res[1]))
    
    if ASSET != 'NONE':
      print('found an asset to buy')
      amount_to_buy = ACCOUNT_TRADE_RATIO * getAmountInAccount(QUOTE_ASSET)
      quantity = formatQuantity(ASSET, amount_to_buy/buy_value)
      if quantity > 0:
        #try:
          order = tradeBuyLimit(ASSET, quantity, buy_value)
          lastBuyOrderID = int(order['orderId'])
          print(order)
          wait_order_count=0
          position = 'pending_buy'
        #except:
        #  position = 'buy'


  if position == 'pending_buy':
      wait_order_count = wait_order_count + 1    
      lastBuyOrder = getOrder(ASSET,lastBuyOrderID)
      print(lastBuyOrder['status'])
      if lastBuyOrder['status'] == 'FILLED' or lastBuyOrder['status'] == 'PARTIALLY_FILLED':
        buy_amount = float(lastBuyOrder['cummulativeQuoteQty'])
        buy_base_qty = FEE*float(lastBuyOrder['executedQty']) #- qty_base_comm_total
        data_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': asset = ' + ASSET + ' buy value = ' + str(buy_value) + ' buy amount = ' + str(buy_amount)
        writeData(data_string, profit)        
        amount_to_sell = buy_amount
        trade_count+=1
        position = 'sell'
      if lastBuyOrder['status'] == 'REJECTED' or lastBuyOrder['status'] == 'EXPIRED' or lastBuyOrder['status'] == 'CANCELED':
        position = 'buy'
      if wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        cancelOrder(lastBuyOrderID)
        position = 'buy'

  if position == 'sell':
    res = preSellLogic(buy_value)
    if res[0]:
      sell_value = formatPrice(ASSET,float(res[1]))
      buy_base_qty = formatQuantity(ASSET, buy_base_qty)
      order = tradeSellLimit(ASSET, buy_base_qty, sell_value)
      lastSellOrderID = int(order['orderId'])

    wait_order_count=0
    print(order)
    position = 'pending_sell'


  if position == 'pending_sell':
      wait_order_count = wait_order_count + 1    
      lastSellOrder = getOrder(ASSET,lastSellOrderID)
      if lastSellOrder['status'] == 'FILLED' or lastSellOrder['status'] == 'PARTIALLY_FILLED':
        sell_amount = float(lastSellOrder['cummulativeQuoteQty'])
        profit *= sell_amount/buy_amount
        print(profit)

        if sell_amount/buy_amount > 1:
          success_count+=1
        
        data_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': asset = ' + ASSET + ' sell amount = ' + str(sell_amount)
        print(str(datetime.now().time()) + ': profit = {0:.3f}   success rate = {1:.3f}]'.format(profit, success_count/trade_count)) 
        writeData(data_string, profit)

        if lastSellOrder['status'] == 'FILLED':
          position = 'buy'
        if lastSellOrder['status'] == 'PARTIALLY_FILLED':
          amount_to_sell = amount_to_sell - sell_amount
          position = 'sell'
      if lastSellOrder['status'] == 'REJECTED' or lastSellOrder['status'] == 'EXPIRED' or lastSellOrder['status'] == 'CANCELED':
        print('cancel order, rejected or expired')
        position = 'sell'
      if wait_order_count > WAIT_ORDER_OPEN_MAX_ITER:
        cancelOrder(ASSET,lastSellOrderID)
        print('cancel order: ',lastSellOrderID)
        wait_order_count = float('-inf')
        position = 'pending_sell'

  if position == 'wait':
      if wait_count_sec > 0:
        wait_count_sec -= 1
      else:
        position = 'buy'

  time.sleep(SLEEP_STEP_SEC)
