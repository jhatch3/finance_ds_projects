import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


ticker_input = "AAPL"
period_input = "1y"

data = yf.download(
    tickers=ticker_input,
    period=period_input)["Adj Close"]



