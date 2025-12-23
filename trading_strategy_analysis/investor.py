"""
Docstring for investor
Author Justin Hatch:

This file includes the Investor class that conducts and tracks trades for each strategy.

Attributes:
    - Stragtegy - Buy and & hold or SMA 
    - Cash - starting bank roll
    - Shares - used when buying / selling
    - Total - cash * shares
    - Trades - meta data of each trade made
    - ar_return - 

Functions:
    place_order(investor: Investor, action: str, date: str, price: float, shares: float = 0.0)
        - buy(investor: Investor, date: str, price: float, shares: float)
        - sell(investor: Investor, date: str, price: float)
    
    place_order calls either buy or sell based on the passed action argument


"""






"""
trade = {
    "type": "buy",          # "buy" or "sell"
    "date": date,           # pd.Timestamp
    "price": price,         # execution price 
    "shares": shares,       # number of shares - not yet
    "total": price * shares, - not yet
}

"""

class Investor:
    def __init__(self, strategy, cash=10_000):
        self.strategy = strategy
        self.cash = float(cash)
        self.shares = 0.0
        self.position_open = False
        self.trades = []
        self.ar_return = 0.0 

def buy(investor: Investor, date: str, price: float, shares: float):
    if investor.position_open:          # can't buy twice
        return 0
    if shares <= 0:
        return 0

    cost = shares * price
    if cost > investor.cash:            # can't buy what you can't afford
        return 0

    investor.cash -= cost
    investor.shares = shares           
    investor.position_open = True

    investor.trades.append({
        "type": "buy", 
        "date": date,
        "price": price,
        "shares": shares, 
        "total": cost
    })
    return 1


def sell(investor: Investor, date: str, price: float):
    if not investor.position_open:      # can't sell twice in a row
        return 0
    if investor.shares <= 0:
        return 0

    proceeds = investor.shares * price
    investor.cash += proceeds

    investor.trades.append({
        "type": "sell", 
        "date": date, 
        "price": price,
        "shares": investor.shares, 
        "total": proceeds
    })

    investor.shares = 0.0
    investor.position_open = False
    return 1


def place_order(investor: Investor, action: str, date: str, price: float, shares: float = 0.0):
    action = action.lower()
    if action == "buy":
        buy(investor, date, price, shares)
        return 1
    elif action == "sell":
        sell(investor, date, price)
        return 1
    else:
        return 0 


if __name__ == "__main__":
        
    inv = Investor("foo", cash=10_000)

    place_order(inv, "buy",  "2025-01-12", price=100, shares=50) 
    place_order(inv, "buy",  "2025-01-13", price=101, shares=10) 
    place_order(inv, "sell", "2025-01-14", price=110)             
    place_order(inv, "sell", "2025-01-15", price=111)             

    print(inv.cash, inv.shares, inv.position_open)
    print(inv.trades)
