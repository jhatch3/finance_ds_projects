"""
Docstring for Helper functions
Author Justin Hatch:

This file includes the functions that help run back testing 

Functions:
    - plot_buy_sell()
    - calc_cagr()

"""



import pandas as pd 
import numpy as np 
import yfinance as yf 
import os
import platform

def plot_buy_sell(ax, data, action: str, date: str, line: str = "Open"):
    """ 
    Plots either buy or sell indicators on any date, on any line.
    
    Args:
        - ax: fig, ax = plt.subplots()
        - action: Str -> example "Buy", "Sell"
        - date: Str -> see data.index for yfiance.download() for further examples on date formating
        - line: Str -> default is Open, can plot on SMA_Open_50 or SMA_Open_255
    """

    # Standardize action and date    
    action = action.lower()
    date = pd.to_datetime(date)

    # if date isnt in df get nearest date in future or raise index error
    if date not in data.index: 
        idx = data.index.get_indexer([date], method="backfill")[0]

        if idx == -1:
            raise IndexError(f"Date: {date} not in df can not find date") 

        date = data.index[idx]

    # Change "SMA_OPEN_50" to somthing else if you want to change where indicator is placed
    price = data.loc[date, line]

    # If label is alread plotted no need to plot again 
    label = "Sell" if action == "sell" else "Buy"
    labels = ax.get_legend_handles_labels()[1]
    use_label = label if label not in labels else None

    # Plot 
    ax.scatter(
        date, price,
        color="Black",
        marker="v" if action == "sell" else "^",
        s=100, alpha=0.6,
        label=use_label
    )


def calc_cagr(days: int, start_balance: float, end_balance: float, trading_days_per_year: int = 252) -> float:
    """
    Calculates Componded Annual Growth Rate (%) 
    
    Args:
        - days: int -> (date.index[-1] - date.index.index[0]).days
        - start_balance: float -> 10_000.00 (start ammount)
        - end_balance: float -> 123,450.23 (inv.cash)
        - trading_days_per_year: int = 252

    Return:
        float: % not decimal
    """
    
    if days <= 0 or start_balance <= 0 or end_balance <= 0:
        # Return nan (0)
        return np.nan

    return ((end_balance / start_balance) ** (trading_days_per_year / days) - 1) * 100

def populate_data(ticker:str, interval: str="1d", period="max"):
    if not ticker:
        raise ValueError("No Ticker Passed")
    
    ticker = ticker.upper()
    data = yf.download(ticker, interval=interval, period=period)
    
    data["SMA_OPEN_50"] = data["Open"].rolling(window=50).mean()
    data["SMA_OPEN_255"] = data["Open"].rolling(window=255).mean()
    data = data.dropna()

    if len(data.index) < 550:
        print(ticker)
    return data 


def sample_start_end_idx(n_rows: int, min_window: int = 1, rng=np.random.default_rng()):
    """
    Returns (start_idx, end_idx) such that:
    - 0 <= start_idx < end_idx < n_rows
    - end_idx - start_idx >= min_window

    Works safely for any stock with sufficient history.
    """

    # Must have at least min_window + 1 points
    if n_rows <= min_window:
        raise ValueError(f"Not enough data points ({n_rows}) for min_window={min_window}")

    # Start can go up to n_rows - min_window - 1
    start = rng.integers(0, n_rows - min_window)

    # End must be at least start + min_window
    end = rng.integers(start + min_window, n_rows)

    print(f"Trading Days {end-start}")
    return start, end


def clear_screen():
    # Check the operating system name
    if platform.system() == "Windows":
        # Command for Windows
        os.system('cls')
    else:
        # Command for Linux and macOS
        os.system('clear')