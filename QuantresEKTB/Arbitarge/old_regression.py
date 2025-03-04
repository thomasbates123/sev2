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

# Dictionary to store data series from each file
data_series1 = {}

# Read each CSV file and store the relevant data series (last 365 days)
for file in csv_files:
    df = pd.read_csv(file_path1)
    # Assuming the relevant column is named 'changePercent'
    data_series1[file] = df['Return']

# Convert the column to a NumPy array
X1 = np.array(df['Return'].head(180))

# Search for the file in the specified directory
file_path2 = os.path.join(directory, min_col_name)

# Dictionary to store data series from each file
data_series2 = {}

# Read each CSV file and store the relevant data series (last 365 days)
for file in csv_files:
    df = pd.read_csv(file_path2)
    # Assuming the relevant column is named 'changePercent'
    data_series2[file] = df['Return']

# Convert the column to a NumPy array
X2 = np.array(df['Return'].head(180))

# X2 = a + B * X1 + error

X1_with_constant = sm.add_constant(X1)
model = sm.OLS(X2, X1_with_constant).fit()
alpha = model.params[0]
beta = model.params[1]

print("alpha:", alpha)
print("beta:", beta)

# Spread calculation
spread = X2 -beta * X1 - alpha
average = np.mean(spread)
std_dev = np.std(spread)
if std_dev==0:
    raise ValueError

# caclulate the z-score
z_score = (spread - average) / std_dev
mean = np.mean(z_score)