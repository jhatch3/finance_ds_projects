"""
"""
from functions import calc_cagr, plot_buy_sell, populate_data, clear_screen
from investor import Investor
from tickers import tickers 
import pandas as pd 

import random
import matplotlib.pyplot as plt  
from scipy.stats import mannwhitneyu


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
sma_len = []

bh_num_trades = []
bh_cagrs = []
bh_len = []

if __name__ == "__main__":
    for i in (range(EPOCHS)):

        # SMA Strategy
        TICKER_SMA = random.choice(tickers)
        DATA_SMA = populate_data(TICKER_SMA)

        inv_sma = Investor(SMA, cash=CASH, ticker=TICKER_SMA, data=DATA_SMA)
        inv_sma.run_sim(i) 

        sma_num_trades.append(len(inv_sma.trades))
        sma_cagrs.append(inv_sma.cagr)
        sma_len.append(inv_sma.len)

        # Buy & Hold Strategy
        TICKER_BH = random.choice(tickers)
        DATA_BH = populate_data(TICKER_BH)

        inv_bh = Investor(BH, cash=CASH, ticker=TICKER_BH, data=DATA_BH)
        inv_bh.run_sim(i)

        bh_num_trades.append(len(inv_bh.trades))
        bh_cagrs.append(inv_bh.cagr)
        bh_len.append(inv_bh.len)

        clear_screen()
        

    fig, ax = plt.subplots(1,1)
    
    ax.set_title(f"Distribution of Compound Annual Growth Rates\n for SMA and Buy-and-Hold Strategies")
    ax.hist(sma_cagrs, bins="auto", color="red", alpha=0.5, label="SMA")
    ax.hist(bh_cagrs, bins="auto", color="blue", alpha=0.5, label="BH")
    ax.set_xlabel("Compound Annual Growth Rate (%)")
    ax.set_ylabel("Count")

    fig.legend()
    fig.show() 
    fig.savefig("cagr.png")

    fig, ax = plt.subplots(1,1)

    ax.set_title(f"Distribution of Number of Trades for SMA Strategy")
    ax.hist(sma_num_trades, bins="auto", color="red", alpha=0.5,  label="SMA")
    ax.set_xlabel("Number of Trades")
    ax.set_ylabel("Count")

    
    fig.legend()
    fig.show() 
    fig.savefig("trades.png")

    df = pd.DataFrame(
        {
        "bh_cagrs" : bh_cagrs,
        "bh_lens": bh_len,
        "sma_cagrs": sma_cagrs,
        "sma_lens": sma_len,
        "sma_num_trades ":sma_num_trades
        }
    )

    df.to_csv('data.csv')

    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(0)} Had 0 Trades")
    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(1)} Had 1 Trade")
    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(2)} followed Buy & Hold.")
    print(f"Out of {len(sma_num_trades)} trades, {sma_num_trades.count(10)} Had 10 Trades")

    u_statistic, p_value = mannwhitneyu(sma_cagrs, bh_cagrs, alternative='greater')

    # Print the results
    print(f"Mann-Whitney U statistic: {u_statistic:.2f}")
    print(f"P-value: {p_value:.4f}")

    # Interpret the results (using a common significance level of 0.05)
    alpha = 0.05
    if p_value < alpha:
        print("Result: Reject the null hypothesis (there is a significant difference between the distributions).")
    else:
        print("Result: Fail to reject the null hypothesis (there is no sufficient evidence of a significant difference).")