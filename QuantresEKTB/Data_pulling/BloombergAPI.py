import blpapi
from blpapi import SessionOptions, Session
import pandas as pd
from xbbg import blp
from datetime import date, timedelta , datetime
from pathlib import Path
import os
import numpy as np

class BloombergAPI:
    def __init__(self):
        # Define session options
        session_options = SessionOptions()
        session_options.setServerHost('localhost')
        session_options.setServerPort(8194)

        # Start a session
        self.session = Session(session_options)
        if not self.session.start():
            print("Failed to start session.")

        if not self.session.openService("//blp/mktdata"):
            print("Failed to open //blp/mktdata")

        if not self.session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            return None

    def get_current_price(self, ticker):
        ticker = ticker + ' US Equity'
        # Create a request for the current price
        ref_data_service = self.session.getService("//blp/mktdata")
        request = ref_data_service.createRequest("ReferenceDataRequest")
        request.getElement("securities").appendValue(ticker)
        request.getElement("fields").appendValue("PX_LAST")

        # Send the request
        self.session.sendRequest(request)

        # Process the response
        while True:
            event = self.session.nextEvent()
            for msg in event:
                if msg.hasElement("securityData"):
                    security_data = msg.getElement("securityData")
                    for security in security_data.values():
                        field_data = security.getElement("fieldData")
                        if field_data.hasElement("PX_LAST"):
                            return field_data.getElementAsFloat("PX_LAST")
            if event.eventType() == blpapi.Event.RESPONSE:
                break

        return None
    
    def get_intraday_data(self, ticker, start_time, end_time):
        # Create a request for intraday data
        ref_data_service = self.session.getService("//blp/refdata")
        request = ref_data_service.createRequest("IntradayBarRequest")
        request.set("security", ticker)
        request.set("eventType", "TRADE")
        request.set("startDateTime", start_time)
        request.set("endDateTime", end_time)
        request.set("interval", 1)  # 1-minute interval

        # Send the request
        self.session.sendRequest(request)

        # Process the response
        data = []
        while True:
            event = self.session.nextEvent()
            for msg in event:
                if msg.hasElement("barData"):
                    bar_data = msg.getElement("barData").getElement("barTickData")
                    for i in range(bar_data.numValues()):
                        bar = bar_data.getValueAsElement(i)
                        data.append({
                            "time": bar.getElementAsDatetime("time"),
                            "open": bar.getElementAsFloat("open"),
                            "high": bar.getElementAsFloat("high"),
                            "low": bar.getElementAsFloat("low"),
                            "close": bar.getElementAsFloat("close"),
                            "volume": bar.getElementAsInteger("volume")
                        })
            if event.eventType() == blpapi.Event.RESPONSE:
                break

        return pd.DataFrame(data)

    def get_intraday_data_for_tickers(self, tickers):
        # Get the current script's directory
        self.repo_root = Path(__file__).resolve().parent.parent  # Adjust as needed

        # Define the intraday data directory relative to the repo
        self.intraday_data_dir = self.repo_root / "Data_pulling" / "IntraDayData"

        # Make sure the directory exists
        self.intraday_data_dir.mkdir(parents=True, exist_ok=True)

        # Delete existing .csv files in the intraday data directory
        file_list = os.listdir(self.intraday_data_dir)
        for file_name in file_list:
            if file_name.endswith('.csv'):
                file_path = self.intraday_data_dir / file_name
                os.remove(file_path)
        
        print(f"files in '{self.intraday_data_dir}' deleted")

        # Define the time range for intraday data (first hour of trading for the past 10 days)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)
        start_time = start_time.replace(hour=9, minute=30, second=0, microsecond=0)
        end_time = end_time.replace(hour=16, minute=00, second=0, microsecond=0)

        # Retrieve intraday data for each ticker and save to .csv files
        for ticker in tickers:
            data = self.get_intraday_data(ticker + ' US Equity', start_time, end_time)
            file_path = self.intraday_data_dir / f"{ticker}.csv"
            data.to_csv(file_path, index=False)
            print(f"Intraday data for {ticker} saved to {file_path}")
    
    
    def get_historic_data(self, tickers):
        # Get the current script's directory
        self.repo_root = Path(__file__).resolve().parent.parent  # Adjust as needed

        # Define the data directory relative to the repo
        self.data_dir = self.repo_root / "Data_pulling" / "Data"

        # Make sure the directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.end_date = date.today().strftime('%Y-%m-%d')
        self.start_date = (date.today() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        file_list = os.listdir(self.data_dir)

        # Iterate over the files and delete the ones with .csv extension
        for file_name in file_list:
            if file_name.endswith('.csv'):
                file_path = self.data_dir / file_name
                os.remove(file_path)
                
        
        print(f"files in '{self.data_dir}' deleted")

        # Retrieve historical data for each ticker
        for ticker in tickers:
            data = blp.bdh(tickers=ticker + ' US Equity', flds=['PX_LAST', 'CHG_PCT_1D'], start_date=self.start_date, end_date=self.end_date)
            
            file_path = self.data_dir / f'{ticker}.csv'
            data.to_csv(file_path)

        print(f"files in '{self.data_dir}' saved")
        csv_files = self.data_dir.glob("*.csv")

        # Iterate over each CSV file
        for csv_file in csv_files:
            # Read the CSV file into a DataFrame
            data = pd.read_csv(csv_file)

            # Remove the first row
            data = data.iloc[1:]
            # Rename the columns
            data.columns = ['Date', 'Price', 'Return']
            data['Price'] = pd.to_numeric(data['Price'])
            data['Log_Price'] = np.log(data['Price'])
            # Calculate the returns on log price
            data['LogReturns'] = data['Log_Price'].diff()
    
            # Save the modified data back to the CSV file
            data.to_csv(csv_file, index=False)
        print(f"files in '{self.data_dir}' modified")
    
    def real_time_price(self, ticker):
        if isinstance(ticker, np.float64):
            ticker = str(ticker)
        if ticker.endswith('.csv'):
            ticker = ticker.replace('.csv', '')
        ticker = ticker + ' US Equity'
        # Create a subscription list
        subscriptions = blpapi.SubscriptionList()

        # Add the ticker to the subscription list with the fields you want to subscribe to
        subscriptions.add(ticker, ["LAST_PRICE"], "", blpapi.CorrelationId(ticker))

        # Subscribe to the real-time data
        self.session.subscribe(subscriptions)

        # Process the real-time data
        while True:
            event = self.session.nextEvent()
            for msg in event:
                if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                    if msg.hasElement("LAST_PRICE"):
                        price = msg.getElementAsFloat("LAST_PRICE")
                        # Unsubscribe after getting the price
                        self.session.unsubscribe(subscriptions)
                        return price  # Return the current tick price and stop
                    
    def get_volatility(self, ticker):
       if isinstance(ticker, np.float64):
           ticker = str(ticker)
       if ticker.endswith('.csv'):
           ticker = ticker.replace('.csv', '')
       ticker = ticker + ' US Equity'

       # Create a request for historical volatility
       request = self.refDataService.createRequest("ReferenceDataRequest")
       request.getElement("securities").appendValue(ticker)
       request.getElement("fields").appendValue("30DAY_VOLATILITY")

       # Send the request
       self.session.sendRequest(request)

       # Process the response
       while True:
           event = self.session.nextEvent()
           for msg in event:
               if event.eventType() == blpapi.Event.RESPONSE:
                   securityDataArray = msg.getElement("securityData")
                   for securityData in securityDataArray.values():
                       fieldData = securityData.getElement("fieldData")
                       if fieldData.hasElement("30DAY_VOLATILITY"):
                           return fieldData.getElement("30DAY_VOLATILITY").getValue()
           if event.eventType() == blpapi.Event.RESPONSE:
               break
       return None



#example usages
if __name__ == '__main__':
    bloomberg = BloombergAPI()
    tickers = ["AAPL", "GOOGL", "MSFT"]
    #bloomberg.get_intraday_data_for_tickers(tickers)
    #ticker = 'AAPL'
    #price = bloomberg_api.real_time_price(ticker)
    #print(f"Real-time price of {ticker}: {price}")
#
    #volatility = bloomberg_api.get_volatility(ticker)
    #print(f"30-day historical volatility of {ticker}: {volatility}")
    
#download data from a set of tickers 
#tickers = ['AAPL', 'GOOGL', 'MSFT', 'XOM', 'BKR', 'BP', 'COP', 'CSIQ', 'CVX', 'DVN', 'ENB', 'HAL', 'KMI', 'NEE', 'SHEL', 'SLB', 'TTE', 'VLO', 'WMB']
#bloomberg_api = BloombergAPI()
#bloomberg_api.get_historic_data(tickers)

# Example usage
#ticker = 'AAPL'
#bloomberg_api = BloombergAPI()
#current_price = bloomberg_api.real_time_price(ticker)
#print(f"The current tick price of {ticker} is {current_price}")


