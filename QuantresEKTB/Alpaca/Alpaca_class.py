# Alpaca/Alpaca_class.py
import alpaca_trade_api as tradeapi
import pandas as pd
from pathlib import Path
import sys
import numpy as np

# Add the directory containing BloombergAPI.py to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'Data_pulling'))
from BloombergAPI import BloombergAPI

bloomberg = BloombergAPI()

class AlpacaTrader:
    def __init__(self, api_key, api_secret, base_url):
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        self.open_trades = pd.DataFrame(columns=['AssetA', 'QtyA', 'AssetB', 'QtyB'])

    def place_order(self, symbol, qty, side, order_type, time_in_force):
        clock = self.api.get_clock()
        try:
            if clock.is_open:
                order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type=order_type,
                    time_in_force=time_in_force  # ioc = immediate or cancel, gtc = good till cancel, fok = fill or kill
                )
                print(f"Order submitted: {order}")
                return order
            else:
                print("The market is closed.")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

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

    def close_order(self, order_id):
        try:
            self.api.cancel_order(order_id)
            print(f"Order {order_id} has been closed.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def close_position(self, symbol , qty):
        try:
            self.api.close_position(symbol=symbol, qty=qty)
            print(f"Order {order_id} has been closed.")
        except Exception as e:
            print(f"An error occurred: {e}")

    
    def pairs_trade(self, symbol1, symbol2, beta, z_score, order_type, time_in_force, append_to_csv=True):
        try:

            account = self.api.get_account()
            available_cash = float(account.cash)
            
            # Get the current price of the two assets
            PriceA = bloomberg.real_time_price(symbol1)
            PriceB = bloomberg.real_time_price(symbol2)
            print(f"Price of {symbol1}: {PriceA}")
            print(f"Price of {symbol2}: {PriceB}")
            beta = float(beta)
            print(f"beta: {beta}")

            Trade_value = available_cash * 0.02
            Trade_value = float(Trade_value)
            PriceA = float(PriceA)
            PriceB = float(PriceB)
            print(f"Trade value: {Trade_value}")  

            QtyA = 0
            QtyB = 0    

            if z_score > 1.5:  # sell A buy B
                print(f"Variables: {Trade_value}, {PriceA}, {PriceB}, {beta}")
                QtyA = Trade_value / PriceA
                QtyB = Trade_value / PriceB * beta
                print(f"QtyA: {QtyA}")
                print(f"QtyB: {QtyB}")
            
                order1 = self.place_order(symbol=symbol1,qty=int(QtyA),side='sell',order_type=order_type,time_in_force=time_in_force)
                order2 = self.place_order(symbol=symbol2,qty=int(QtyB),side='buy',order_type=order_type,time_in_force=time_in_force)
            
            elif z_score < -1.5:  # sell B buy A
                print(f"Variables: {Trade_value}, {PriceA}, {PriceB}, {beta}")
                QtyA = Trade_value / PriceA * beta
                QtyB = Trade_value / PriceB
                print(f"QtyA: {QtyA}")
                print(f"QtyB: {QtyB}")
                order1 = self.place_order(symbol=symbol1,qty=int(QtyA),side='buy',order_type=order_type,time_in_force=time_in_force)
                order2 = self.place_order(symbol=symbol2,qty=int(QtyB),side='sell',order_type=order_type,time_in_force=time_in_force) 

            print(f"QtyA: {QtyA}")
            print(f"QtyB: {QtyB}")        

            AssetA = symbol1
            QtyA = QtyA
            AssetB = symbol2
            QtyB = QtyB

            # Create the new trade DataFrame
            new_trade = pd.DataFrame([{
                'AssetA': AssetA,
                'QtyA': QtyA,
                'AssetB': AssetB,
                'QtyB': QtyB
            }])

            # Append the trade
            self.append_trade(new_trade, append_to_csv)

        except Exception as e:
            print(f"An error occurred: {e}")

    def append_trade(self, new_trade, append_to_csv):
        try:
            # Append the results to the DataFrame
            self.open_trades = pd.concat([self.open_trades, new_trade], ignore_index=True)
            print(f"Order submitted: {new_trade}")

            if append_to_csv:
                # Define the path to the CSV file in the "Orders" directory
                repo_root = Path(__file__).resolve().parent.parent  # Adjust as needed
                orders_dir = repo_root / "Arbitarge" / "Orders"
                orders_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
                csv_file = orders_dir / "trades.csv"

                # Check if the CSV file exists
                if csv_file.exists():
                    # Read the existing data and append the new trade
                    existing_trades = pd.read_csv(csv_file)
                    updated_trades = pd.concat([existing_trades, new_trade], ignore_index=True)
                else:
                    # Create a new CSV file with the new trade
                    updated_trades = new_trade

                # Save the updated DataFrame back to the CSV file
                updated_trades.to_csv(csv_file, index=False)
                print(f"Trades saved to {csv_file}")

        except Exception as e:
            print(f"An error occurred while appending to CSV: {e}")

    def pairs_close_position(self, symbol1, symbol2):
        try:
            # Get the current script's directory
            repo_root = Path(__file__).resolve().parent.parent  # Adjust as needed
            # Define the data directory relative to the repo
            data_dir = repo_root / "Arbitarge" / "Orders"
            csv_file = data_dir / "trades.csv"
#
            # Load the DataFrame from the CSV file if it exists
            if csv_file.exists():
                self.open_trades = pd.read_csv(csv_file)
            else:
                print(f"No trades file found at {csv_file}")
                return
#
            # Find the row corresponding to the given pair of tickers
            trade = self.open_trades[(self.open_trades['AssetA'] == symbol1) & (self.open_trades['AssetB'] == symbol2)]
            if trade.empty:
                print(f"No open trade found for {symbol1} and {symbol2}")
                return
#
            AssetA = trade['AssetA'].values[0]
            AssetB = trade['AssetB'].values[0]
            qtyA = int(trade['QtyA'].values[0])
            qtyB = int(trade['QtyB'].values[0])

            # Remove the row from the DataFrame
            self.open_trades = self.open_trades.drop(trade.index)
#
            # Reverse the trade by placing a new order with opposite quantities
            self.place_order(symbol=AssetA, qty=qtyA, side='sell', order_type='market', time_in_force='gtc')
            self.place_order(symbol=AssetB, qty=qtyB, side='buy', order_type='market', time_in_force='gtc')
#
            # Save the updated DataFrame back to the CSV file
            self.open_trades.to_csv(csv_file, index=False)
            print(f"Position closed and removed for {symbol1} and {symbol2}")
#
        except Exception as e:
            print(f"An error occurred: {e}")
        

    def get_open_pairs(self):
        try:
            # Get the current script's directory
            repo_root = Path(__file__).resolve().parent.parent  # Adjust as needed
            # Define the data directory relative to the repo
            data_dir = repo_root / "Arbitarge" / "Orders"
            csv_file = data_dir / "trades.csv"

            # Load the DataFrame from the CSV file if it exists
            if csv_file.exists():
                self.open_trades = pd.read_csv(csv_file)
            else:
                print(f"No trades file found at {csv_file}")
                return []

            # Extract pairs
            pairs = self.open_trades[['AssetA', 'AssetB']].values.tolist()
            return pairs

        except Exception as e:
            print(f"An error occurred: {e}")
            return [] 

    def save_open_trades(self, filename):
         # Get the current script's directory
         repo_root = Path(__file__).resolve().parent.parent  # Adjust as needed
         # Define the data directory relative to the repo
         data_dir = repo_root / "Arbitarge" / "Orders"
         filepath = data_dir / filename
         self.open_trades.to_csv(filepath, index=False)
         print(f"Open trades saved to {filepath}")

        
        




if __name__ == '__main__':
    API_KEY = 'PKQX6GG42DF7OHRVLY03'
    API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
    BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading

    alpaca = AlpacaTrader(API_KEY, API_SECRET, BASE_URL)
    #alpaca.close_order('fb02e879-be77-4acc-bb5b-c22f338d3aee')
    
    # Example usage
    #alpaca.pairs_trade('AAPL', 'GOOGL', 10, 10, 'market', 'gtc')
    #alpaca.pairs_trade('AAPL', 'MSFT', 10, 10, 'market', 'gtc')
    #alpaca.pairs_trade('AAPL', 'GOOGL', 1.5 , -2.1, 'market', 'gtc')
    #alpaca.pairs_trade('XOM', 'HAL', 10, 10, 'market', 'gtc')
    #alpaca.pairs_trade('AAPL', 'HAL', 10, 10, 'market', 'gtc')
    #alpaca.pairs_trade('JKS', 'XOM', 10, 10, 'market', 'gtc')
    #alpaca.pairs_trade('COP', 'DVN', 10, 10, 'market', 'gtc')
    #alpaca.pairs_trade('OXY', 'MPC', 10, 10, 'market', 'gtc')
    #alpaca.pairs_close_position('AAPL', 'GOOGL')
    # alpaca.close_order('722be7c5-6026-4b8c-8282-c25ea6647166')
    # alpaca.close_position('AAPL')
    #alpaca.view_open_positions()







