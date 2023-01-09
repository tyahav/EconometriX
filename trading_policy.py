import yahoofinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import scipy.fftpack
from scipy.signal import find_peaks
# import datetime as dt
from trading_simulator import *
def output_trading_prices(stkSer):
    WINDOW_ANALYSIS_DAYS = stkSer.shape[0]

    MEAN_WINDOW_DAYS = 5
    rm = stkSer.rolling(window=MEAN_WINDOW_DAYS)
    stkSerNorm = (stkSer - rm.mean())

    stkSerNorm = stkSerNorm / rm.mean()
    stkSerNorm = stkSerNorm.dropna()
    winStart = stkSer.index[MEAN_WINDOW_DAYS]
    # winStart = pd.to_datetime('2018-06-01')
    # tDel = pd.to_timedelta(WINDOW_ANALYSIS_DAYS, unit='days')
    WinEnd = stkSer.index[-1]
    tDel = WinEnd - winStart

    N = len(stkSerNorm[winStart:])

    stkNormFFT = np.fft.fft(stkSerNorm[winStart:])

    E = abs(np.sqrt(sum(stkNormFFT * np.conj(stkNormFFT))))
    #
    # i = abs(stkNormFFT) > 0
    # stkNormFFTLowFreq = stkNormFFT[1:10]

    # filter periods by cycle duration and amplitude
    # MAX_PERIOD = WINDOW_ANALYSIS_DAYS / 2
    # MIN_PERIOD = WINDOW_ANALYSIS_DAYS / 8
    MAX_PERIOD = 30
    MIN_PERIOD = 12

    MIN_RELATIVE_AMP = 0.3

    ks = np.arange(0,N)
    # k_all = np.arange(0,N)

    per = 2*np.pi*N/ks
    perAmpNorm = max(abs(stkNormFFT))
    perNorm = abs(stkNormFFT) / perAmpNorm
    spec_norm = np.abs(stkNormFFT)

    i =  (per > MIN_PERIOD) * (per < MAX_PERIOD) * (perNorm > MIN_RELATIVE_AMP)
    best_per_idx = np.argmax(spec_norm[i])
    # best_per_idx = np.argmax()
    # if i == []
    k = np.arange(0,N)[i]
    best_k = k[best_per_idx]
    # perFiltered = per[k]

    # orgVals = stkSerNorm[winStart:(WinEnd + tDel)].values
    # t = np.arange(1, len(orgVals),0.1)


    # print(2*np.pi*1/(k/N))

    # A = abs(stkSerNorm.values[k])
    # Atot = abs(A.sum())
    # A = A / Atot

    # C = 0.5*(stkNormFFT[k] + np.conj(stkNormFFT[N-k-1]))

    # def CycFunc(t):
    #   res = np.array([])
    #   for ti in t:
    #     res = np.append(res,(A*np.real(stkNormFFT[k]*np.exp(1j*ti*k/N))).sum())
    #   return res


    orgValsPast = stkSerNorm[winStart:].values

    xMax,yMax = find_peaks(orgValsPast, height=0)
    yMaxValues = np.array(list(yMax.values()))
    yMaxMean = yMaxValues.mean()

    xMin,yMin = find_peaks(orgValsPast*(-1), height=0)
    yMinValues = np.array(list(yMin.values()))  * (-1)
    yMinMean = yMinValues.mean()

    # meanProfitRel = yMaxMean - yMinMean
    # C = 0.5*(stkNormFFT[k] + np.conj(stkNormFFT[N-k-1]))
    return yMinMean, yMaxMean, 2*np.pi*N/best_k

def main():
    historical = yf.HistoricalPrices('MSFT', '2017-01-01', '2020-01-01')
    dfs = historical.to_dfs()
    df = dfs['Historical Prices']
    df.index = pd.to_datetime(df.index)
    # trial = df.tail(90)
    start = pd.to_datetime('2019-03-01') - pd.to_timedelta(5 ,unit='days')
    end = start + pd.to_timedelta(95,unit='days')

    trial = df[start:end]
    a,b, period = output_trading_prices(trial['Close'])
    print(a, b, period)
    test = df[end-pd.to_timedelta(5,unit='days'): end+pd.to_timedelta(95,unit='days')]
    simple_trading_simulator(a, b, test['Close'])


if __name__ == "__main__":
    main()
