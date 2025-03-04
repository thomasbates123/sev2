
API_KEY = 'PKQX6GG42DF7OHRVLY03'
API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
BASE_URL = 'https://paper-api.alpaca.markets' 

from Alpaca_class import AlpacaTrader

API_KEY = 'PKQX6GG42DF7OHRVLY03'
API_SECRET = '1WJCeCDThAagVtxObjeq46zEbweTabSgaEJ8DjVP'
BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading

trader = AlpacaTrader(API_KEY, API_SECRET, BASE_URL)

# Place an order
trader.place_order('AAPL', 10, 'sell', 'market', 'gtc')

# View open orders
#trader.view_open_orders()

#trader.view_open_positions()

# View active assests
#trader.active_assets()
 

#trader.close_order('AAPL')
#trader.close_position('AAPL' , 10 ) 
