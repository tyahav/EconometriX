# import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt

Money = 1 # dollars

# actions = {'Action Start Time': [dt.datetime(2019,8,10) , dt.datetime(2019,10,11)],'Action Duration': [dt.timedelta(days=60) , dt.timedelta(days=45)], 'Ticker' : ['MSFT', 'AAPL'], 'Buy Limit': [234, 10], 'Sell Limit' : [250, 80], 'Action Status' : ['P','P']}
# df = pd.DataFrame(data=actions)

#
# tickers = df['Ticker'].values
# tickersStr = ''
# for t in tickers:
#   tickersStr += t +' '
#
#
# TIME_DELTA_PAD = np.timedelta64(1,'D')
# minActStart= np.min(df['Action Start Time'].values)
# maxActEnd = np.max(df['Action Start Time'].values + df['Action Duration'].values)
#
# minActStart = minActStart - TIME_DELTA_PAD
# maxActEnd = maxActEnd + TIME_DELTA_PAD
#
# data = yf.download(tickersStr, start=pd.to_datetime(minActStart).strftime("%Y-%m-%d"), end=pd.to_datetime(maxActEnd).strftime("%Y-%m-%d"))
#
# for i in df.index:
#   actionStartTime = df['Action Start Time'][i]
#   actionEndTime = actionStartTime + df['Action Duration'][i]
#   tkr = df['Ticker'][i]
#   buyLimit = df['Buy Limit'][i]
#   sellLimit = df['Sell Limit'][i]
#   highs = data['High'][tkr][actionStartTime:actionEndTime]
#   lows = data['Low'][tkr][actionStartTime:actionEndTime]
#   # buyOptions =
#   #typ = df['Type'][i]

def simple_trading_simulator(minVal, maxVal, stkSer):
  MEAN_WINDOW_DAYS = 5
  rm = stkSer.rolling(window=MEAN_WINDOW_DAYS)
  stkSerNorm = (stkSer[1:] - rm.mean())
  stkSerNorm = stkSerNorm / rm.mean()
  stkSer = stkSer[1:]
  # stkSerNorm = stkSerNorm.dropna()
  bought = False
  buyVals = []
  sellVals = []
  buyInds = []
  sellInds = []
  for i in range(MEAN_WINDOW_DAYS,stkSerNorm.shape[0]):
    if stkSerNorm[i] <= minVal and bought==False:
      bought = True
      buyVals.append(stkSer[i])
      buyInds.append(i)
    elif stkSerNorm[i] > maxVal and bought==True:
    # if bought == True and stkSer[i] >= buyVals[-1]*(1+maxVal-minVal):
      bought = False
      sellVals.append(stkSer[i])
      sellInds.append(i)

  if len(buyInds) > len(sellInds):
    buyInds = buyInds[:-1]
    buyVals = buyVals[:-1]

  print(np.array(sellInds) - np.array(buyInds))
  print(buyVals)
  print(sellVals)
  print((np.array(sellVals) - np.array(buyVals))/np.array(buyVals))

