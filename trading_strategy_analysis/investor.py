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

from functions import calc_cagr, plot_buy_sell, populate_data, sample_start_end_idx

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt     


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
    def __init__(self, strategy, data,  ticker, cash=10_000):
        self.ticker = ticker
        self.data = data
        self.strategy = strategy
        self.cash = float(cash)
        self.shares = 0.0
        self.position_open = False
        self.trades = []
        self.cagr = 0
        self.start_ammount = float(cash) 

    def buy(self, date: str, price: float, shares: float):
        if self.position_open:          # can't buy twice
            return 0
        if shares <= 0:
            return 0

        cost = shares * price
        if cost > self.cash:            # can't buy what you can't afford
            return 0

        self.cash -= cost
        self.shares = shares           
        self.position_open = True

        self.trades.append({
            "type": "buy", 
            "date": date,
            "price": price,
            "shares": shares, 
            "total": cost
        })
        return 1


    def sell(self, date: str, price: float):
        if not self.position_open:      # can't sell twice in a row
            return 0
        if self.shares <= 0:
            return 0

        proceeds = self.shares * price
        self.cash += proceeds

        self.trades.append({
            "type": "sell", 
            "date": date, 
            "price": price,
            "shares": self.shares, 
            "total": proceeds
        })

        self.shares = 0.0
        self.position_open = False
        return 1


    def place_order(self, action: str, date: str, price: float, shares: float = 0.0):
        action = action.lower()
        if action == "buy":
            self.buy(date, price, shares)
            return 1
        elif action == "sell":
            self.sell(date, price)
            return 1
        else:
            return 0 
    
    def run_bh_sim(self) -> float:
        
        stock = self.ticker
        
        
        start, end = sample_start_end_idx(n_rows=len(self.data))

        df = self.data.iloc[start:end].copy()
        
        date = df.index[0]
        self.place_order("buy",  date, price=df.loc[date]["Open"][stock], shares= (self.cash // df.loc[date]["Open"][stock] - 1))

        date = df.index[-1]
        self.place_order("sell",  date, price=df.loc[date]["Open"][stock])



        if self.position_open:
            print(f"Closing")
            self.place_order("sell",  df.index[-1], price=df.loc[df.index[-1]]["Open"][stock])


    
        days = (df.index[-1] - df.index[0]).days  
        cagr = calc_cagr(days=days, start_balance=self.start_ammount, end_balance=self.cash) 
        self.cagr = cagr 
        return cagr 

    def run_sma_sim(self) -> float:
            
            stock = self.ticker

            cooldown_days = 1

            start, end = sample_start_end_idx(n_rows=len(self.data))

            df = self.data.iloc[start:end].copy()


            # Spread and sign
            spread = df["SMA_OPEN_50"] - df["SMA_OPEN_255"]
            sign = np.sign(spread)

            # Cross happens when sign changes (ignore zeros by forward filling)
            # Thanks CHAT for this holy 
            sign = sign.replace(0, np.nan).ffill()
            cross = sign.ne(sign.shift(1))  # True on crossover dates
            cross_dates = df.index[cross.fillna(False)]

            last_plotted_date = None

            for date in cross_dates:
                if last_plotted_date is None or (date - last_plotted_date).days >= cooldown_days:
                    # Determine direction of cross:
                    # if spread goes from negative -> positive => golden cross (buy)
                    prev_spread = spread.loc[:date].iloc[-2] if spread.loc[:date].shape[0] >= 2 else -1
                    curr_spread = spread.loc[date]

                    if prev_spread < 0 and curr_spread > 0:
                        if  self.place_order("buy",  date, price=df.loc[date]["Open"][stock], shares= (self.cash // df.loc[date]["Open"][stock] - 1)):
                            last_plotted_date = date

                    elif prev_spread > 0 and curr_spread < 0:
                        if self.place_order("sell",  date, price=df.loc[date]["Open"][stock]):
                            last_plotted_date = date

            if self.position_open:
                self.place_order("sell",  df.index[-1], price=df.loc[df.index[-1]]["Open"][stock])
            
            days = (df.index[-1] - df.index[0]).days 
            cagr = calc_cagr(days=days, start_balance=self.start_ammount, end_balance=self.cash)
            self.cagr = cagr 
            return cagr
    

    def run_sim(self):
        """
        :param stock:
        """
        
        if self.strategy == "Buy & Hold":
            self.run_bh_sim() 

        elif self.strategy == "SMA": 
            self.run_sma_sim()

        else:
            raise ValueError("Enter 'Buy & Hold' or 'SMA' for trading strategy")
    
if __name__ == "__main__":

    BH = "Buy & Hold"
    SMA = "SMA"
    CASH = 10_000   
    TICKER = "AAPL"
    DATA = populate_data(TICKER)

    inv = Investor(BH, cash=CASH, ticker=TICKER, data=DATA)

    inv.run_sim() 
            

    print(inv.cash, inv.shares, inv.position_open)
    print(inv.trades)

    
    
    