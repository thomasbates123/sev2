import blpapi
from blpapi import SessionOptions, Session, Service, Request

# Bloomberg API session setup
session_options = SessionOptions()
session_options.setServerHost('localhost')
session_options.setServerPort(8194)

session = Session(session_options)

if not session.start():
    print("Failed to start session.")
    exit()

if not session.openService("//blp/refdata"):
    print("Failed to open //blp/refdata")
    exit()

refDataService = session.getService("//blp/refdata")

def get_bdp(ticker, field):
    request = refDataService.createRequest("ReferenceDataRequest")
    request.getElement("securities").appendValue(ticker)
    request.getElement("fields").appendValue(field)
    
    session.sendRequest(request)
    
    while True:
        ev = session.nextEvent()
        for msg in ev:
            if msg.hasElement("securityData"):
                securityDataArray = msg.getElement("securityData")
                for securityData in securityDataArray.values():
                    fieldData = securityData.getElement("fieldData")
                    if fieldData.hasElement(field):
                        return fieldData.getElement(field).getValue()
        if ev.eventType() == blpapi.Event.RESPONSE:
            break
    return None

# Fetch underlying asset data
underlying_ticker = 'AAPL US Equity'

# Current stock price
S = get_bdp(underlying_ticker, 'PX_LAST')
if S is None:
    print("Failed to retrieve current stock price.")
    exit()



# Historical volatility (30-day)
sigma = get_bdp(underlying_ticker, '30DAY_VOLATILITY')
if sigma is None:
    print("Failed to retrieve historical volatility.")
    exit()
sigma /= 100

# Risk-free rate (3-month Treasury yield)
rf_ticker = 'USGG3M Index'
r = get_bdp(rf_ticker, 'PX_LAST')
if r is None:
    print("Failed to retrieve risk-free rate.")
    exit()
r /= 100

print(f"Current stock price (S): {S}")
print(f"Dividend yield (q): {q}")
print(f"Historical volatility (sigma): {sigma}")
print(f"Risk-free rate (r): {r}")

# Stop the session
session.stop()