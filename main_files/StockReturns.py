from base_file.base import Properties as props
import yfinance as yf
import pandas as pd
import time
import os
import datetime

#yf.download("Tesla, Inc. ", start='2024-12-01',end='2025-01-01')


# Example: Download historical prices for Tesla
class Returns:
    def __init__(self):
        self.returnsdataOutput = props.outputPath
        self.ticker = props.stockName
        self.tickersymbol = props.stockTicker
        self.stockPortfolio = props.stockPortfolio
        self.marketReturns = props.marketPortfolio
        self.rfReturns = props.rfReturns
        
    def calc_daily_stock_returns(self,startdate,enddate):
        try:
            #tickersymbol = self.tickersymbol
            # stock = yf.Ticker(tickersymbol)
            # data = stock.history(start=startdate, end=enddate)
            data = pd.read_csv(self.stockPortfolio)
            data['Date'] = pd.to_datetime(data['Date'])
            #data = yf.download(ticker, start=startdate,end=enddate )
            data['daily_returns'] = (data['Close'] - data['Close'].shift(1))/data['Close'].shift(1) *100
            #drop row with NA
            data = data.dropna()
            data_final = data[['Date','Close','daily_returns']]

            data_final.columns = ['Date','stock_close','daily_returns']
            data_final = data_final.reset_index()
            #data_final['Date'] = data_final['Date'].dt.tz_localize(None)
            print(data_final.shape)
            print("---stock returns",data_final.head())
            return data_final
        except Exception as e:
            print(f"Error in daily stock returns : {e}")


    def calc_daily_risk_free_rate(self):
        try:
            #add the risk free rates
            rf_rate = pd.read_csv(self.rfReturns)
            rf_rate['Date'] = pd.to_datetime(rf_rate['Date'])
            rf_rate['rf_change'] = rf_rate['Returns']*100
            print("---risk free rate",rf_rate.head())
            return rf_rate
        except Exception as e:
            print(f"Error in Risk Free rate : {e}")

    def calc_daily_market_return(self,startdate,enddate):
        try:
            #Use s&p 500 as a proxy for market returns
            #sp500 = yf.download("^GSPC", start=startdate, end=enddate)
            sp500 = pd.read_csv(self.marketReturns)
            sp500['Date'] = pd.to_datetime(sp500['Date'])
            sp500['Close'] = sp500['Close'].str.replace(',','').astype(float)
            sp500['market_returns'] = (sp500['Close'] - sp500['Close'].shift(1))/sp500['Close'].shift(1) *100
            sp500 = sp500.dropna()
            sp500_final = sp500[['Date','Close','market_returns']]

            sp500_final.columns = ['Date','market_close','market_returns']
            sp500_final = sp500_final.reset_index()
            print(sp500_final.shape)
            print("---sp500",sp500_final.head())
            return sp500_final
        except Exception as e:
            print(f"Error market returns : {e}")

    def combine_returns(self,startdate,enddate):
        try:
            rt = Returns()
            stock_return = rt.calc_daily_stock_returns(startdate,enddate)
            rf_rate = rt.calc_daily_risk_free_rate()
            sp500 = rt.calc_daily_market_return(startdate,enddate)

            #combine the dataframes on date
            combined = pd.merge(stock_return,sp500,how='inner',on='Date')
            rf_rate['Date'] = pd.to_datetime(rf_rate['Date'])
            combined1 = pd.merge(combined,rf_rate[['Date','rf_change']],how='inner',on='Date')
            combined1['excess_market_returns'] = combined1['market_returns'] - combined1['rf_change']
            combined1['excess_stock_returns'] = combined1['daily_returns'] - combined1['rf_change']
            combined1.columns = combined1.columns.str.upper()

            print(combined1.head())
            print(combined1.shape)
            combined1.to_csv(self.returnsdataOutput + "calculated_returns.csv",index=False)
            return combined1
        except Exception as e:
            print(f"combining sections : {e}")