import datetime
import yfinance as yf
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl

import lxml.html
import requests
import datetime as dt

#from sec_edgar_downloader import Downloader
#from edgar import Company, XBRL, XBRLElement
from pandas import Series, DataFrame

print("Hello World!")

pastFurtureFactor = 4
tdFuturePrediction = datetime.timedelta(days=90.0)
tdPast = tdFuturePrediction * pastFurtureFactor
gIndex = 1

dtStartPeriod = dt.datetime(year=2008,month=1,day=1)
dtDataPeriod = datetime.timedelta(days=365)
#dtEndPeriod = dtStartPeriod + dtDataPeriod
STOCKS_SCAN_PERIOD_YEARS = 10
STOCKS_SCAN_INTERVAL_MONTHS = 1 # Note options in function
dfStockValuesLabled = DataFrame(columns=['StockName', 'StartTime', 'Period', 'StockAtStart', 'StockAtEnd','LableTime', 'LableValue'])

# Tickers to read
dfTickers = pd.read_csv("Nasdaq100_TickersOnly.csv")

for tickerIndex in range(dfTickers.count()[0]):
    ### Start Generating Data
    tickerName = dfTickers.iloc[tickerIndex]['Ticker']
    tickerData = yf.Ticker(tickerName)
    dfStockData = tickerData.history(period=str(STOCKS_SCAN_PERIOD_YEARS)+"y", start=dtStartPeriod,interval=str(STOCKS_SCAN_INTERVAL_MONTHS)+"mo")
    dtStartTmp = dtStartPeriod

    for t in range(STOCKS_SCAN_PERIOD_YEARS):
        dfPeriodStrockData = dfStockData.loc[dtStartTmp:(dtStartTmp+dtDataPeriod)]
        if not (dfPeriodStrockData.empty):
            openValueAtPeriodStart =  dfPeriodStrockData.iloc[1]['Open']
            closeValueAtPeriodEnd = dfPeriodStrockData.iloc[dfPeriodStrockData.count()[0]-1]['Close']

            lable = (closeValueAtPeriodEnd - openValueAtPeriodStart) / ((openValueAtPeriodStart+closeValueAtPeriodEnd)/2)
            dfStockValuesLabled.loc[gIndex]=[tickerName, dtStartTmp, dtDataPeriod, openValueAtPeriodStart,closeValueAtPeriodEnd,dtStartTmp+dtDataPeriod+tdFuturePrediction, lable]
            gIndex+=1

        dtStartTmp += dtDataPeriod

dfStockValuesLabled.to_csv("LabledStocks_Nasdaq100.csv")

print("Done")


#dl = Downloader("C:/Users/tomya_000/Desktop/StockX/Filings")
#dl.get("10-Q", "MSFT", 1)

#company = Company("MICROSOFT CORP", "0000789019")
#tree = company.get_filings_url(filing_type="10-Q",prior_to="2019-12-31")
#docs = Company.get_documents(tree, no_of_documents=10)

# edgar_address = r"https://www.sec.gov/cgi-bin/browse-edgar"

# edgar_params = {'action' : 'getcompany',
#                 'CIK': '0000789019',
#                 'type' : '10-Q',
#                 'owner' : 'exclude',
#                 'start' : '',
#                 'output' : 'atom',
#                 'count' : '10'
# }

#response = requests.get(url=edgar_address, params = edgar_params)

#print(response.status_code)
#print(response.text)


#lxml.html.open_in_browser(docs[0])
#print(df.iloc[[2,5],:])


