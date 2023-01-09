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

def tradeBuyLimit(buy_amount, buy_price):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=BUY")
  q.append("type=LIMIT")
  q.append("timeInForce=IOC")
  q.append("quantity="+str(buy_amount/buy_price))
  q.append("price	="+str(buy_price))
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

def tradeSellLimit(sell_amount, sell_price):
  tss = str(int(time.time()*1000))
  q = []
  q.append("symbol="+SYMBOL)
  q.append("side=SELL")
  q.append("type=LIMIT")
  q.append("timeInForce=IOC")
  q.append("quantity="+str(sell_amount/sell_price))
  q.append("price	="+str(sell_price))
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
    if ord['orderId'] == orderId:
      return ord
  
  return {'status' : 'NA'}

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


# Script Configuration
BASE = "https://testnet.binance.vision/api"
SLEEP_STEP_SEC = 60
SLEEP_POSITION_SEC = 60*5

HEAD = {'X-MBX-APIKEY' : 'YyoNDKmcWxvmwJGqb4N0V1X3nKyOoblaCIv22aubfwnNlW5JuJW48jczYRJPEsMO'}
KEY = 'kFGM6IDQwUBcSwcNBXd82aVDQ0kJGYul7XoRwelzDSj8BHcboK3ELYjIe8C1Apnq'

bkey = KEY.encode('utf-8')

# Trade parameters
SYMBOL = "BNBUSDT"

BASE_ASSET='BNB'
QUOTE_ASSET='USDT'


ARB = 0.001
LOOK_BACK_TIME_MIN = 60 * 1
DROP_TO_BUY =  2 * ARB
DROP_TO_SELL = 1 * ARB
PRICE_COUNT_LIMIT_BUY = 5
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
      amount_to_buy = getAmountInAccount(QUOTE_ASSET)
      j = tradeBuyLimit(amount_to_buy, current_val)
      lastBuyOrderID = int(j['orderId'])
      buy_value = current_val
      position = 'pending_buy'

  if position == 'sell':
    if current_val/buy_value-1 > ARB or 1-current_val/buy_value > min(DROP_TO_SELL, (profit**(SELL_PROFIT_EXP))*DROP_TO_SELL):
      amount_to_sell = getAmountInAccount(BASE_ASSET)
      max_sell_value_allowed = float(getFilterValue(SYMBOL,'MARKET_LOT_SIZE')['maxQty'])
      
      if (amount_to_sell > max_sell_value_allowed):
        amount_to_sell = max_sell_value_allowed

      j = tradeSellLimit(amount_to_sell, current_val)
      lastSellOrderID = int(j['orderId'])
      sell_value = current_val
      position = 'pending_sell'


  if position == 'pending_buy':    
      lastBuyOrder = getOrder(lastBuyOrderID)
      if lastBuyOrder['status'] == 'FILLED' or lastBuyOrder['status'] == 'PARTIALLY_FILLED':
        buy_amount = float(lastBuyOrder['cummulativeQuoteQty'])
        data_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : buy value = ' + str(buy_value) + ' buy amount = ' + str(buy_amount)
        writeData(data_string, profit)        
        position = 'sell'
      if lastBuyOrder['status'] == 'REJECTED' or lastBuyOrder['status'] == 'EXPIRED' or lastBuyOrder['status'] == 'CANCELED':
        position = 'buy'
  
  if position == 'pending_sell':    
      lastSellOrder = getOrder(lastSellOrderID)
      if lastSellOrder['status'] == 'FILLED':
        sell_amount = float(lastSellOrder['cummulativeQuoteQty'])
        profit *= sell_amount/buy_amount
        data_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : sell value = ' + str(sell_value) + ' sell amount = ' + str(sell_amount) + '\n' + str(datetime.now().time()) + ' : *** profit = ' + str(profit)
        writeData(data_string, profit)        
        position = 'buy'
      if lastSellOrder['status'] == 'PARTIALLY_FILLED':
        position = 'sell'
      if lastSellOrder['status'] == 'REJECTED' or lastSellOrder['status'] == 'EXPIRED' or lastSellOrder['status'] == 'CANCELED':
        position = 'sell'

  prev_values.append(current_val)
  time.sleep(SLEEP_STEP_SEC)