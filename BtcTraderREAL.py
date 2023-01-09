import pandas as pd
import numpy as np
import requests
import io
import time
from datetime import datetime

BASE = "	https://testnet.binance.vision/api"

def getBitcoinPrice():
  dataOK = False
  while not dataOK:
    try:
      response = requests.get(BASE+"/v3/ticker/price",params="symbol="+SYMBOL)
      j = json.loads(response.content.decode("UTF-8"))
      p = float(j['price'])
      dataOK = True
    except:
      time.sleep(1)

  return p

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
  q.append("quoteOrderQty="+str(buy_amount))
  q.append("timestamp="+ tss)

  data = '&'.join(q)
  bdata= data.encode('utf-8')

  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
  return j

def tradeSellMarket(sell_amount):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=SELL")
  q.append("type=MARKET")
  q.append("quantity="+str(sell_amount))
  q.append("timestamp="+ tss)
  data = '&'.join(q)
  bdata= data.encode('utf-8')
  sign = hmac.new(bkey,bdata,hashlib.sha256).hexdigest()
  response = requests.post(BASE+"/v3/order",params=data+"&signature="+sign,headers=HEAD)
  j=json.loads(response.content.decode('UTF-8'))
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
    print(ord['orderId'])
    if ord['orderId'] == orderId:
      return ord
  
  return 'NA'


# Script Configuration
SLEEP_STEP_SEC = 60
SLEEP_POSITION_SEC = 60*5

# Trade parameters
SYMBOL = "BNBUSDT"

QUOTE_ASSET='USDT'
BASE_ASSET='BNB'

ARB = 0.001
LOOK_BACK_TIME_MIN = 60 * 1
DROP_TO_BUY =  2 * ARB
DROP_TO_SELL = 1 * ARB
PRICE_COUNT_LIMIT_BUY = 10
BUY_PROFIT_EXP = 1.0
SELL_PROFIT_EXP = -0.01
PRICE_COUNT_LIMIT_BUY_MAX = 50
PRICE_COUNT_LIMIT_BUY_MINMAX = 15

profit = 1.0


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
      buy_time.append(datetime.now().time())
      amount_to_buy = getAmountInAccount(QUOTE_ASSET)
      j = tradeBuyMarket(amount_to_buy)
      lastBuyOrderID = int(j['orderId'])
      position = 'pending_buy'

  if position == 'sell':
    if current_val/buy_value-1 > ARB or 1-current_val/buy_value > min(DROP_TO_SELL, (profit**(SELL_PROFIT_EXP))*DROP_TO_SELL):
      amount_to_sell = getAmountInAccount(BASE_ASSET)
      j = tradeSellMarket(amount_to_sell)
      lastSellOrderID = int(j['orderId'])
      position = 'pending_sell'


  if position == 'pending_buy':    
      lastBuyOrder = getOrder(lastBuyOrderID)
      if lastBuyOrder['status'] == 'FILLED' or lastBuyOrder['status'] == 'PARTIALLY_FILLED':
        buy_value = float(lastBuyOrder['cummulativeQuoteQty'])
        data_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : buy value = ' + str(buy_value)
        writeData(data_string, profit)        
        position = 'sell'
      if lastBuyOrder['status'] == 'REJECTED' or lastBuyOrder['status'] == 'EXPIRED' or lastBuyOrder['status'] == 'CANCELED':
        position = 'buy'
  
  if position == 'pending_sell':    
      lastSellOrder = getOrder(lastSellOrderID)
      if lastSellOrder['status'] == 'FILLED':
        sell_value = float(lastSellOrder['cummulativeQuoteQty'])
        profit *= sell_value/buy_value
        data_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : sell value = ' + str(sell_value) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
        writeData(data_string, profit)        
        position = 'buy'
      if lastSellOrder['status'] == 'PARTIALLY_FILLED':
        position = 'sell'
      if lastSellOrder['status'] == 'REJECTED' or lastSellOrder['status'] == 'EXPIRED' or lastSellOrder['status'] == 'CANCELED':
        position = 'sell'

  prev_values.append(current_val)
  time.sleep(SLEEP_STEP_SEC)