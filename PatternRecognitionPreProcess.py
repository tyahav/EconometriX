### PATTERN RECOGNITION PRE-PROCESS SCRIPT ###
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Paths for inputs / outputs
DATA_PATH = './DATA/'
OUPUT_PATH = './OUTPUT/'

# Process Parameters
ROLL_WIN_DURATION = '10 min'
TD_ONE_DAY = pd.to_timedelta('1 day')
TD_PATTERN_WINDOW_DUR = pd.to_timedelta('180 min')
TD_PATTERN_WINDOW_SHIFT = pd.to_timedelta('15 min')
STOCK_CHANGE_LIMIT = 0.001

# Script starts here

input_files = os.listdir(path)

for f in input_files:
  # 1. read file and calc rolling mean
  df = pd.read_csv(DATA_PATH+FILE_NAME, index_col=0, names=['Time','Open','Close','High','Low','Vol'], parse_dates=['Time'])
  stk_val_df = (df['High'] + df['Low'])/2
  stk_val_df_mean = stk_val_df.rolling(window=ROLL_WIN_DURATION).mean().dropna()
  trade_dates = pd.to_datetime(stk_val_df_mean.index.strftime("%Y-%m-%d").unique())

  # 2. For each "pattern window" calculate profit and normalize data
  stk_win_data_df = pd.DataFrame(columns=['Date','Duration','Values','Profit','Label'], index=['Time'])

  for d in trade_dates:
    # 2.1. Get a specific trade day data
    daily_stock_values_mean =  stk_val_df_mean[d:d+TD_ONE_DAY]
    t = daily_stock_values_mean.index[0]

    day_start = daily_stock_values_mean.index[0]
    day_end = daily_stock_values_mean.index[-1]
    t = day_start

    # 2.2. Calc a specific trade day pattern windows
    while t + TD_PATTERN_WINDOW_DUR <= day_end:
      win_stock_values = daily_stock_values_mean[t:t+TD_PATTERN_WINDOW_DUR]
      p = win_stock_values.values.max() / win_stock_values[0] - 1
      lbl = p > STOCK_CHANGE_LIMIT

      # *** normalize: substarct mean and devide by max-min:
      win_stock_values_norm = (win_stock_values - win_stock_values.mean()) / (win_stock_values.max() - win_stock_values.min())
      
      row_df = pd.DataFrame({"Date":[d], "Duration":[TD_PATTERN_WINDOW_DUR],"Values":[win_stock_values_norm],"Profit":[p],"Label":[lbl] }, index=[t]) 
      stk_win_data_df = stk_win_data_df.append(row_df)

      t += TD_PATTERN_WINDOW_SHIFT
  stk_win_data_df.to_json(orient="index",path_or_buf=(OUPUT_PATH+f+".json"))
