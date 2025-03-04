# Alpaca/Alpaca_class.py
import alpaca_trade_api as tradeapi

class AlpacaTrader:
    def __init__(self, api_key, api_secret, base_url):
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    def place_order(self, symbol, qty, side, order_type, time_in_force):
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force # ioc = immediate or cancel, gtc = good till cancel , fok fill or kill , d
            )
            print(f"Order submitted: {order}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def view_open_orders(self):
        try:
            orders = self.api.list_orders(status='open')
            if orders:
                print("Open orders:")
                for order in orders:
                    print(order)
            else:
                print("No open orders.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def view_open_positions(self):
        try:
            positions = self.api.list_positions()
            if positions:
                print("Open positions:")
                for position in positions:
                    print(position)
            else:
                print("No open positions.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close_order(self, symbol):
        try:
            self.api.cancel_order(symbol)
            print(f"Order for {symbol} has been closed.")
        except Exception as e:
            print(f"An error occurred: {e}")

API_KEY = 'PKQX6GG42DF7OHRVLY03'
API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
BASE_URL = 'https://paper-api.alpaca.markets' 

import numpy as np
from z_score_regression import beta
from z_score_regression import z_score
from coint_test import min_row_name  
from coint_test import min_col_name
import os

API_KEY = 'PKQX6GG42DF7OHRVLY03'
API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading

trader = AlpacaTrader(API_KEY, API_SECRET, BASE_URL)

# Initialize x2_side and x1_side to None
x2_side = None
x1_side = None

# Ensure min_col_name and min_row_name are defined
ticker1 = os.path.splitext(min_col_name)[0]
ticker2 = os.path.splitext(min_row_name)[0]

print(z_score[-1])

if np.any(z_score[-1] < -1.2):
    # long x2 short beta x1
    long_x2 = True
    x2_side = 'buy'
    x1_side = 'sell'
    print("Long x2, Short beta x1")

elif np.any(z_score[-1] > 1.2):
    # short x2 long beta x1
    long_x2 = False
    x2_side = 'sell'
    x1_side = 'buy'
    print("Short x2, Long beta x1")

else:
    print("No trade signal detected.")
    x2_side = None
    x1_side = None

if x2_side and x1_side:
    # submit order
    trader.place_order(
        symbol=ticker1,
        qty=1,
        side=x2_side,
        time_in_force='gtc',
        order_type='market',
    )

    trader.place_order(
        symbol=ticker2,
        qty=beta,
        side=x1_side,
        time_in_force='gtc',
        order_type='market',
    )
else:
    print("Order not placed due to missing trade signal.")
