import sys
import os
from pathlib import Path
import numpy as np
import threading
import time

# Add the directory containing BloombergAPI.py to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'Data_pulling'))
from BloombergAPI import BloombergAPI

bloomberg = BloombergAPI()


# Add the directory containing Alpaca.py to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'Alpaca'))
from Alpaca_class import AlpacaTrader
API_KEY = 'PKQX6GG42DF7OHRVLY03'
API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading
trader = AlpacaTrader(API_KEY, API_SECRET, BASE_URL)


from Statistcal_Arbitarge import ArbitargeAnalyzer
import time

directory = Path(__file__).resolve().parent.parent / "Data_pulling" / "Data"
analyzer = ArbitargeAnalyzer(data_directory=directory)
analyzer.load_data()
analyzer.calculate_cointegration()


pairs_to_open = analyzer.cointegrated_pairs
#pairs_to_close = trader.get_open_pairs()



# Event to stop the thread
stop_event = threading.Event()

def print_numbers_and_letters():
    while not stop_event.is_set():

        # Check if there are any open pairs 
        pairs_to_close = trader.get_open_pairs()


        while (len(pairs_to_open) > 0 or len(pairs_to_close) > 0) and not stop_event.is_set():
                
                for open_pair in pairs_to_open:
                    if stop_event.is_set():
                        break
                    analyzer.z_score(open_pair[0], open_pair[1])
                    beta = analyzer.z_score(open_pair[0], open_pair[1])[0]
                    print(f"beta: {beta}")
                    z_score = analyzer.z_score(open_pair[0], open_pair[1])[1]
                    print(f"checking to open {open_pair[0]} and {open_pair[1]}")

                    if beta <= 0:
                        continue  # Skip this iteration if beta is negative or zero
                    if np.abs(z_score) > 1:  # sell A buy B 
                        # pairs trade first ticker is bought and second ticker is sold
                        trader.pairs_trade(open_pair[0], open_pair[1], beta, z_score, 'market', 'gtc')
                        print(f"Opening {open_pair[0]} and {open_pair[1]})")
                        pairs_to_open.remove(open_pair)




                for i in range(len(pairs_to_close)):
                    if stop_event.is_set():
                        break
                    AssetA = pairs_to_close[i][0]
                    AssetB = pairs_to_close[i][1]
                    z_score = analyzer.z_score(AssetA,AssetB)[1] 
                    print(f"Checking to close {AssetA} and {AssetB}")
                    if np.abs(z_score) < 0.05:
                        trader.pairs_close_position(AssetB, AssetA)
                        print(f"Closing {AssetA} and {AssetB}")
                    time.sleep(0.1)



# Create thread
number_and_letter_thread = threading.Thread(target=print_numbers_and_letters)

# Start thread
number_and_letter_thread.start()

# Wait for user input to stop the loop
input("Press Enter to stop...\n")

# Signal the thread to stop
stop_event.set()

# Wait for the thread to complete
number_and_letter_thread.join()

print("Thread has finished execution.")



