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

# Function to regress AssetA with AssetB to find beta
def find_beta(assetA, assetB):
    assetA = sm.add_constant(assetA)
    model = sm.OLS(assetB, assetA).fit()
    return model.params.iloc[1]


# ... [Keep all your initial imports and setup code] ...

# Initialize analyzer and find cointegrated pairs
Analyzer = ArbitargeAnalyzer(data_directory=directory)
Analyzer.load_data()
Analyzer.calculate_cointegration(column_name='open')
print("Cointegrated pairs:", Analyzer.cointegrated_pairs)

# Backtest parameters
initial_portfolio = 100000  # Per pair
entry_threshold = 2.0
exit_threshold = 0.05
extreme_exit_threshold = 2.5
risk_per_trade = 0.02  # 2% of portfolio per trade

results = []
all_portfolio_values = []  # To store portfolio values for all pairs

for pair in Analyzer.cointegrated_pairs:
    assetA, assetB = pair
    print(f"\nBacktesting pair: {assetA} vs {assetB}")
    
    # Load data
    dfA = pd.read_csv(directory / f"{assetA}.csv")
    dfB = pd.read_csv(directory / f"{assetB}.csv")
    
    # Align data
    common_dates = dfA.index.intersection(dfB.index)
    dfA = dfA.loc[common_dates]
    dfB = dfB.loc[common_dates]
    
    # Calculate beta and spread
    beta = find_beta(dfA['open'], dfB['open'])
    spread = dfB['open'] - beta * dfA['open']
    mean_spread = spread.mean()
    std_spread = spread.std()
    
    # Initialize trading variables for this pair
    portfolio_value = initial_portfolio
    position = 0  # 1=long, -1=short
    entry_spread = 0
    entry_qtyA = 0
    entry_qtyB = 0
    trade_open = False
    portfolio_history = [portfolio_value]  # Track portfolio value over time
    z_history = []
    
    for i in range(len(spread)):
        current_priceA = dfA.iloc[i]['open']
        current_priceB = dfB.iloc[i]['open']
        current_spread = spread.iloc[i]
        z_score = (current_spread - mean_spread) / std_spread
        z_history.append(z_score)
        
        if not trade_open:
            # Long signal (spread is below mean)
            if z_score < -entry_threshold:
                # Calculate position size (2% of portfolio)
                position_size = portfolio_value * risk_per_trade
                
                # Calculate quantities based on hedge ratio
                entry_qtyB = position_size / current_priceB
                entry_qtyA = (position_size * beta) / current_priceA
                
                # Update cash balance (short A, long B)
                portfolio_value += entry_qtyA * current_priceA  # Proceeds from short
                portfolio_value -= entry_qtyB * current_priceB   # Cost of long
                
                trade_open = True
                position = 1
                entry_spread = current_spread
                print(f"{dfA.index[i]} - OPEN LONG: {assetA} x {beta} vs {assetB}")
                
            # Short signal (spread is above mean)
            elif z_score > entry_threshold:
                position_size = portfolio_value * risk_per_trade
                
                entry_qtyB = position_size / current_priceB
                entry_qtyA = (position_size * beta) / current_priceA
                
                # Update cash balance (long A, short B)
                portfolio_value -= entry_qtyA * current_priceA   # Cost of long
                portfolio_value += entry_qtyB * current_priceB   # Proceeds from short
                
                trade_open = True
                position = -1
                entry_spread = current_spread
                print(f"{dfA.index[i]} - OPEN SHORT: {assetA} x {beta} vs {assetB}")
                
        else:
            # Calculate current position value
            if position == 1:
                # Mark-to-market long position
                mtm_value = (entry_qtyB * current_priceB - entry_qtyA * current_priceA)
            else:
                # Mark-to-market short position
                mtm_value = (-entry_qtyB * current_priceB + entry_qtyA * current_priceA)
            
            # Check exit conditions
            exit_signal = False
            if position == 1:
                if z_score >= exit_threshold or z_score > extreme_exit_threshold:
                    exit_signal = True
            elif position == -1:
                if z_score <= -exit_threshold or z_score < -extreme_exit_threshold:
                    exit_signal = True
            
            if exit_signal:
                # Close position
                if position == 1:
                    portfolio_value += entry_qtyB * current_priceB  # Close long B
                    portfolio_value -= entry_qtyA * current_priceA  # Cover short A
                else:
                    portfolio_value -= entry_qtyB * current_priceB  # Cover short B
                    portfolio_value += entry_qtyA * current_priceA  # Close long A
                
                pnl = portfolio_value - portfolio_history[-1]
                print(f"{dfA.index[i]} - CLOSE POSITION | PnL: ${pnl:.2f}")
                
                trade_open = False
                position = 0
                entry_qtyA = 0
                entry_qtyB = 0
        
        # Record portfolio value
        portfolio_history.append(portfolio_value)
    
    # Store results for this pair
    results.append({
        'pair': f"{assetA}-{assetB}",
        'final_value': portfolio_value,
        'returns': (portfolio_value - initial_portfolio) / initial_portfolio,
        'max_drawdown': (np.array(portfolio_history).min() - initial_portfolio) / initial_portfolio,
        'portfolio_history': portfolio_history,
        'z_scores': z_history
    })
    
    # Append portfolio history for aggregate PnL calculation
    all_portfolio_values.append(portfolio_history)

# Aggregate PnL Calculation
# Align all portfolio histories to the same length
min_length = min(len(history) for history in all_portfolio_values)
aligned_portfolios = [history[:min_length] for history in all_portfolio_values]

# Sum portfolio values across all pairs
aggregate_portfolio = np.sum(aligned_portfolios, axis=0)

# Calculate aggregate PnL
initial_aggregate_value = initial_portfolio * len(Analyzer.cointegrated_pairs)
aggregate_pnl = aggregate_portfolio - initial_aggregate_value

# Plot Aggregate PnL
plt.figure(figsize=(12, 6))
plt.plot(aggregate_pnl, label='Aggregate PnL')
plt.title("Aggregate Profit/Loss Across All Pairs")
plt.xlabel("Time")
plt.ylabel("PnL ($)")
plt.legend()
plt.grid(True)
plt.show()

# Display aggregate results
print("\nAggregate Results:")
print(f"Initial Aggregate Capital: ${initial_aggregate_value:,.2f}")
print(f"Final Aggregate Value: ${aggregate_portfolio[-1]:,.2f}")
print(f"Total Aggregate PnL: ${aggregate_pnl[-1]:,.2f}")