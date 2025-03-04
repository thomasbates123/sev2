import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
import matplotlib.pyplot as plt
import sys

# Define the directory containing the CSV files
directory = Path(__file__).resolve().parent.parent / "Data_pulling" / "IntraDayData"

# Add the directory containing BloombergAPI.py to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'Arbitarge'))
from Statistical_Arbitarge import ArbitargeAnalyzer

Analyzer = ArbitargeAnalyzer(data_directory=directory)
Analyzer.load_data()
Analyzer.calculate_cointegration(column_name = 'open')
print(Analyzer.coint_matrix)
print(Analyzer.cointegrated_pairs)

# Function to regress AssetA with AssetB to find beta
def find_beta(assetA, assetB):
    assetA = sm.add_constant(assetA)
    model = sm.OLS(assetB, assetA).fit()
    return model.params.iloc[1]


portfolio_value = 100000
# Find all CSV files in the directory
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
data_series = {}
spread_df = pd.DataFrame(columns=['AssetA', 'AssetB', 'Beta', 'Mean Spread', 'Std Spread'])

for pair in Analyzer.cointegrated_pairs:
    assetA = pair[0]
    assetB = pair[1]

    data_series[assetA] = pd.read_csv(directory / f"{assetA}.csv")
    data_series[assetB] = pd.read_csv(directory / f"{assetB}.csv")

    # Ensure the data is aligned
    assetA_data = data_series[assetA]['open']
    assetB_data = data_series[assetB]['open']

    min_length = min(len(assetA_data), len(assetB_data))
    assetA_data = assetA_data[:min_length]
    assetB_data = assetB_data[:min_length]

    assetA_data = sm.add_constant(assetA_data)
    model = sm.OLS(assetB_data, assetA_data).fit()
    beta = model.params.iloc[1]

    if beta <= 0:
        continue  

    spread = assetB_data - beta * assetA_data['open']
    mean_spread = spread.mean()
    std_spread = spread.std()

    row_df = pd.DataFrame({
        'AssetA': [assetA],
        'AssetB': [assetB],
        'Beta': [beta],
        'Mean Spread': [mean_spread],
        'Std Spread': [std_spread]
    })   

    spread_df = pd.concat([spread_df, row_df], ignore_index=True)

    entry_threshold = 2.0
    exit_threshold = 0.05
    extreme_exit_threshold = 3.5  # Initial portfolio value

    signals = pd.Series(0, index=assetA_data.index)
    position = 0  # 1 for long, -1 for short, 0 for no position
    entry_price = 0
    entry_qtyA = 0
    entry_qtyB = 0
    pnl = 0
    pnl_series = pd.Series(0, index=assetA_data.index)
    trade_open = False  # Flag to indicate if a trade is open
    portfolio_values = []

    z_values = []
    for k in range(len(assetA_data)):
        spread = assetB_data.iloc[k] - beta * assetA_data.iloc[k]
        z_value = (spread - mean_spread) / std_spread
        z_value = z_value['open']
        print(portfolio_value)
        if not trade_open:
            if z_value >= 2:
                # Long signal - sell A and Buy B]
                qtyA = portfolio_value*0.02 / assetA_data.iloc[k]
                qtyB = portfolio_value*0.02 / (assetB_data.iloc[k]*beta)
                type = 'long'
                cost = qtyA * assetA_data.iloc[k] - qtyB * assetB_data.iloc[k]

                portfolio_value = portfolio_value - cost
                trade_open = True

            elif z_value <= -2:
                # Short signal - Buy A and Sell B
                qtyA = portfolio_value*0.02 / assetA_data.iloc[k]
                type = 'short'
                cost = -qtyA * assetA_data.iloc[k] + qtyB * assetB_data.iloc[k]

                portfolio_value = portfolio_value - cost
                trade_open = True

        elif trade_open:
            if z_value <= 0.05 or z_value >= 3.5:
                #close the trade
                if type == 'long':
                    profit = - qtyA * assetA_data.iloc[k] + qtyB * assetB_data.iloc[k]
 
                    portfolio_value = portfolio_value + profit
                    trade_open = False
                
                elif type == 'short':
                    profit = qtyA * assetA_data.iloc[k] - qtyB * assetB_data.iloc[k]

                    portfolio_value = portfolio_value + profit
                    trade_open = False
        portfolio_values.append(portfolio_value)


plt.figure(figsize=(10, 6))
plt.plot(assetA_data.index, portfolio_values, label='Portfolio Value')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.title('Portfolio Value Over Time')
plt.legend()
plt.show()        





    


  


