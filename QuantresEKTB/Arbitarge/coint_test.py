import os
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint
from pathlib import Path

# Directory containing the CSV files
directory = Path(__file__).resolve().parent.parent / "Data_pulling" / "Data"

# Make sure the directory exists
directory.mkdir(parents=True, exist_ok=True)

# Find all CSV files in the directory
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

print(f"Directory: {directory}")
print(f"CSV files found: {csv_files}")

# Dictionary to store data series from each file
data_series = {}
print(data_series)

# Read each CSV file and store the relevant data series (last 365 days)
for file in csv_files:
    file_path = os.path.join(directory, file)
    df = pd.read_csv(file_path)
    data_series[file] = df['Log_Price']

coint_matrix = pd.DataFrame(index=csv_files, columns=csv_files)

# Calculate the cointegration test statistic between each pair of time series
for i in range(len(csv_files)):
    for j in range(i, len(csv_files)):
        series1 = data_series[csv_files[i]]
        series2 = data_series[csv_files[j]]
        print(f"Performing cointegration test between {csv_files[i]} and {csv_files[j]}")
        # Ensure the series have the same length
        min_length = min(len(series1), len(series2))
        series1 = series1[:min_length]
        series2 = series2[:min_length]
        try:
            coint_t, p_value, critical_values = coint(series1, series2)
            coint_matrix.iloc[i, j] = p_value
            coint_matrix.iloc[j, i] = p_value  # Cointegration matrix is symmetric
            print(f"Cointegration test statistic: {p_value}")
        except Exception as e:
            print(f"Error performing cointegration test between {csv_files[i]} and {csv_files[j]}: {e}")

print("Cointegration Matrix:")
print(coint_matrix)

# Convert the matrix to a NumPy array and find the smallest absolute value
coint_matrix_np = coint_matrix.to_numpy().astype(float)
np.fill_diagonal(coint_matrix_np, np.nan)  # Ignore diagonal values
min_abs_value = np.nanmin(np.abs(coint_matrix_np))

# Find the indices of the smallest absolute value
min_indices = np.where(np.abs(coint_matrix_np) == min_abs_value)
min_row_index = min_indices[0][0]
min_col_index = min_indices[1][0]

# Get the corresponding row and column names
min_row_name = coint_matrix.index[min_row_index]
min_col_name = coint_matrix.columns[min_col_index]

print("Smallest absolute value in the cointegration matrix:")
print(min_abs_value)
print(f"Row: {min_row_name}, Column: {min_col_name}")





