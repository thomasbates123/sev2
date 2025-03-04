
from BloombergAPI import BloombergAPI
from datetime import date, timedelta


bloomberg = BloombergAPI()


# Define the tickers
tickers = ['XOM', 'CVX', 'COP', 'OXY', 'MPC', 'EOG', 'JKS', 'DVN', 'APA', 'SLB', 'HAL', 'BKR', 'NOV','FTI', 'KMI', 'WMB', 'ET', 'OKE', 'TGRP','AAPL','GOOGL']

bloomberg.get_historic_data(tickers)
bloomberg.get_intraday_data_for_tickers(tickers)
#MRO not acive anymore aquired by COP


