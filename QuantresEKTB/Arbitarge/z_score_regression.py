import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from coint_test import min_row_name  
from coint_test import min_col_name
from coint_test import csv_files
from coint_test import directory

# Search for the file in the specified directory
file_path1 = os.path.join(directory, min_row_name)
file_path2 = os.path.join(directory, min_col_name)

# Read the CSV files
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)

# Assuming the relevant column is named 'Return'
data_series1 = df1['Return'].head(180).dropna()
data_series2 = df2['Return'].head(180).dropna()

# Ensure both series have the same length
min_length = min(len(data_series1), len(data_series2))
data_series1 = data_series1[:min_length]
data_series2 = data_series2[:min_length]

# Convert the columns to NumPy arrays
X1 = np.array(data_series1)
X2 = np.array(data_series2)

# Add a constant to the independent variable
X2_with_const = sm.add_constant(X2)

# Perform the regression
model = sm.OLS(X1, X2_with_const).fit()

beta = model.params[1]

# Spread calculation
spread = X2 - beta * X1
average = np.mean(spread)
std_dev = np.std(spread)
if std_dev==0:
    raise ValueError

# caclulate the z-score
z_score = (spread - average) / std_dev
mean = np.mean(z_score)