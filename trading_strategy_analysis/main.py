"""
"""
from functions import calc_cagr, plot_buy_sell, populate_data, clear_screen
from investor import Investor
from tickers import tickers 
from tqdm import tqdm

import random
import matplotlib.pyplot as plt  

import os
import platform

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


EPOCHS  = 200
CASH = 10_000   


BH = "Buy & Hold"
SMA = "SMA"

sma_num_trades = []
sma_cagrs = []

bh_num_trades = []
bh_cagrs = []

if __name__ == "__main__":
    for i in (range(EPOCHS)):

        # SMA Strategy
        TICKER_SMA = random.choice(tickers)
        DATA_SMA = populate_data(TICKER_SMA)

        inv_sma = Investor(SMA, cash=CASH, ticker=TICKER_SMA, data=DATA_SMA)
        inv_sma.run_sim() 

        sma_num_trades.append(len(inv_sma.trades))
        sma_cagrs.append(inv_sma.cagr)
        

        # Buy & Hold Strategy
        TICKER_BH = random.choice(tickers)
        DATA_BH = populate_data(TICKER_BH)

        inv_bh = Investor(BH, cash=CASH, ticker=TICKER_BH, data=DATA_BH)
        inv_bh.run_sim()

        bh_num_trades.append(len(inv_bh.trades))
        bh_cagrs.append(inv_bh.cagr)
   
        clear_screen()
        

    fig, ax = plt.subplots(2,1)
    
    ax[0].set_title(f"Distribution of Compound Annual Growth Rates (CAGR) for SMA and Buy-and-Hold Strategies")
    ax[0].hist(sma_cagrs, bins="auto", color="red", alpha=0.5, label="SMA")
    ax[0].hist(bh_cagrs, bins="auto", color="blue", alpha=0.5, label="BH")
    ax[0].set_xlabel("Compound Annual Growth Rate (%)")
    ax[0].set_ylabel("Count")

    ax[1].set_title(f"Number of Trades  SMA ")
    ax[1].hist(sma_num_trades, bins="auto", color="red", alpha=0.5)
    ax[1].set_xlabel("Distribution of Number of Trades for SMA Strategy")
    ax[1].set_ylabel("Count")

    
    fig.set_size_inches([25,15])
    fig.legend()
    fig.show() 
    fig.savefig("photo.png")

    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(0)} Had 0 Trades")
    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(1)} Had 1 Trade")
    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(2)} followed Buy & Hold.")
    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(10)} Had 10 Trades")