import os
import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import warnings
import sys

# Add the directory containing BloombergAPI.py to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'Data_pulling'))
from BloombergAPI import BloombergAPI

bloomberg = BloombergAPI()


# Add the directory containing Alpaca.py to sys.path
#sys.path.append(str(Path(__file__).resolve().parent.parent / 'Alpaca'))
#from Alpaca_class import AlpacaTrader
#API_KEY = 'PKQX6GG42DF7OHRVLY03'
#API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
#BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading
#trader = AlpacaTrader(API_KEY, API_SECRET, BASE_URL)


class ArbitargeAnalyzer:
    def __init__(self, data_directory, threshold=0.05):
        self.data_directory = Path(data_directory)
        self.threshold = threshold
        self.data_series = {}
        self.coint_matrix = None
        self.coint_triangular = None
        self.cointegrated_pairs = []
        self.spreads = {}  # Initialize the spreads dictionary

    def load_data(self):
            # Make sure the directory exists
            self.data_directory.mkdir(parents=True, exist_ok=True)
    
            # Load all CSV files from the directory
            csv_files = [f for f in os.listdir(self.data_directory) if f.endswith('.csv')]
    
            # Read each CSV file into a pandas DataFrame and store it in the dictionary
            for csv_file in csv_files:
                file_path = self.data_directory / csv_file
                df = pd.read_csv(file_path)
                self.data_series[csv_file] = df
    
            # Initialize the cointegration matrix
            num_files = len(csv_files)
            self.coint_matrix = pd.DataFrame(np.zeros((num_files, num_files)), index=csv_files, columns=csv_files)


    def calculate_cointegration(self, column_name='Price'):
        # Silence warnings
        warnings.filterwarnings("ignore")

        # Create an empty DataFrame to store the cointegration matrix
        csv_files = list(self.data_series.keys())
        self.coint_matrix = pd.DataFrame(index=csv_files, columns=csv_files)

        # Read each CSV file and store the relevant data series (last 365 days)
        data_series = {}
        for file in csv_files:
            df = self.data_series[file]
            if column_name in df.columns:
                data_series[file] = df[column_name]
            else:
                raise ValueError(f"Column '{column_name}' not found in file '{file}'")

        # Calculate the cointegration test statistic between each pair of time series
        for i in range(len(csv_files)):
            for j in range(i, len(csv_files)):
                series1 = data_series[csv_files[i]]
                series2 = data_series[csv_files[j]]
                min_length = min(len(series1), len(series2))
                series1 = series1[:min_length]
                series2 = series2[:min_length]
                coint_t, p_value, critical_values = coint(series1, series2)
                self.coint_matrix.iloc[i, j] = p_value
                self.coint_matrix.iloc[j, i] = 0  # Cointegration matrix is symmetric
                np.fill_diagonal(self.coint_matrix.values, np.inf)
                if p_value < self.threshold and p_value != 0:
                    self.cointegrated_pairs.append((csv_files[i].replace('.csv', ''), csv_files[j].replace('.csv', '')))


    def z_score(self, ticker1, ticker2):
        ticker1 = str(ticker1)
        ticker2 = str(ticker2)        

        if not ticker1.endswith('.csv'):
            ticker1 += '.csv'
        if not ticker2.endswith('.csv'):
            ticker2 += '.csv'

        series_ticker1 = self.data_series[ticker1]['Price']
        series_ticker2 = self.data_series[ticker2]['Price']

        # Align the two series by date
        aligned_data = pd.concat([series_ticker1, series_ticker2], axis=1, join='inner').dropna()
        series_ticker1 = aligned_data.iloc[:, 0]
        series_ticker2 = aligned_data.iloc[:, 1]

        # Regress series_ticker2 on series_ticker1
        #series1 ~ sergeis2
        model = sm.OLS(series_ticker1, sm.add_constant(series_ticker2))
        results = model.fit()
        spread_ratio = results.params[1]

        spread = series_ticker1 - spread_ratio * series_ticker2
        current_spread = bloomberg.real_time_price(ticker1) - spread_ratio * bloomberg.real_time_price(ticker2)

        z_score = (current_spread - np.mean(spread)) / np.std(spread)
        return spread_ratio,z_score
        
        
    
    def run_analysis(self):
        self.load_data()
        self.calculate_cointegration()


if __name__ == '__main__':
    # Create an instance of CointegrationAnalyzer
    directory = Path(__file__).resolve().parent.parent / "Data_pulling" / "IntraDayData"
    analyzer = ArbitargeAnalyzer(data_directory=directory)
    analyzer.load_data()
    analyzer.calculate_cointegration( column_name= "open")
    print(analyzer.coint_matrix)




#if __name__ == '__main__':
#    # Create an instance of CointegrationAnalyzer
#    directory = Path(__file__).resolve().parent.parent / "Data_pulling" / "Data"
#    analyzer = ArbitargeAnalyzer(data_directory=directory)
#    analyzer.load_data()
#    analyzer.calculate_cointegration()
#    print(analyzer.coint_matrix)
#    print(analyzer.cointegrated_pairs)
#    print(analyzer.z_score('AAPL', 'GOOGL'))
#
#    analyzer.calculate_cointegration()
#    pairs_to_open = analyzer.cointegrated_pairs
#    print(f"Pairs to open: {pairs_to_open}")
#
