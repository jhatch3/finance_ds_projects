import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Global variable 
BACK_TEST = True
BACK_TEST_DAYS = 30

def compute_log_returns(df):
    prices = df.iloc[:, 0].astype(float)

    # Remove zero or negative values
    prices = prices.replace([0], np.nan)
    prices = prices[prices > 0]
    prices = prices.dropna()

    # Compute log returns
    log_returns = np.log(prices / prices.shift(1))
    df = log_returns.to_frame(name="logReturns").dropna()
    return df 

def get_returns_df(ticker:str, period:str= "max"):
    # Download data and return as pd "Date, Returns"

    try:
        data = yf.download(
            tickers=ticker,
            period=period)
        
        if data is None or data.empty:
            print(f"No data returned for ticker: '{ticker}'.")
            return pd.DataFrame()
        
        raw_df = data["Close"].pct_change().dropna()
        raw_df = raw_df.reset_index().set_index("Date")
        clean_df = raw_df.set_axis(['Returns'], axis=1)
        return clean_df 
    
    except ValueError as e:
        print(f"Error Downloading Data: {e}")
        return pd.DataFrame()

def split_df(df, x:int=BACK_TEST_DAYS):
    split_date = datetime.now() - timedelta(days=x)
    split_date = split_date.strftime("%Y-%m-%d")

    train = df.loc[:split_date]
    test  = df.loc[split_date:]
    
    return train, test

def calc_anualized_mu(df):
    mu_daily = df["logReturns"].mean()
    return mu_daily * 252
 

def calc_anualized_sigma(df):
    sigma_daily = df["logReturns"].std()
    return sigma_daily * np.sqrt(252) 

def run_sim(mu, sigma, df, number_of_sims=100, dt=1, n_days = 30):
    
    last_price = df["logReturns"].iloc[-1]
    n_days = 30
    data = {}
    for i in range(number_of_sims):
        prices = [last_price]
        for _ in range(n_days):
            eps = np.random.normal()
            next_price = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt 
                                            + sigma * np.sqrt(dt) * eps)
            prices.append(next_price)

        data[f"Sim_{i}"] = prices

    sim_df = pd.DataFrame(data)
    return sim_df

if __name__ == "__main__":
    ticker_input = "AAPL"
    period_input = "1y"

    train_data = get_returns_df("AAPL")

    if BACK_TEST:
        train_data, test_data = split_df(train_data)
        
    log_returns_df = compute_log_returns(train_data)

    anualized_mu = calc_anualized_mu(log_returns_df)
    anualized_sigma = calc_anualized_mu(log_returns_df) 
    df = run_sim(anualized_mu, anualized_sigma, train_data)
    print(df)