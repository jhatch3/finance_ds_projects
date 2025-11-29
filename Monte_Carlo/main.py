import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Global variable 
BACK_TEST = True
BACK_TEST_DAYS = 30

def get_df(ticker:str, period:str= "max"):
    # Download data and return as pd "Date, Returns"

    try:
        data = yf.download(
            tickers=ticker,
            period=period)
        
        if data is None or data.empty:
            print(f"No data returned for ticker: '{ticker}'.")
            return pd.DataFrame()
        
        data.columns = [col[0] for col in data.columns]
        return data 
    
    except ValueError as e:
        print(f"Error Downloading Data: {e}")
        return pd.DataFrame()



def calc_anualized_mu(df):
    mu_daily = df["logReturns"].mean()
    return mu_daily * 252
 
def calc_anualized_sigma(df):
    sigma_daily = df["logReturns"].std()
    return sigma_daily * np.sqrt(252) 

def run_sim(mu_annual, sigma_annual, df, number_of_sims=10, days=100):
    
    # Find day 0 price 
    last_price = df.tail(days).iloc[0]["Close"]

    # Convert annual to daily
    mu_daily = mu_annual / 252.0
    sigma_daily = sigma_annual / np.sqrt(252.0)

    dt = 1.0  # 1 trading day

    data = {}
    for i in range(number_of_sims):
        prices = [last_price]
        for _ in range(days):
            eps = np.random.normal()
            next_price = prices[-1] * np.exp(
                (mu_daily - 0.5 * sigma_daily**2) * dt
                + sigma_daily * np.sqrt(dt) * eps
            )
            prices.append(round(next_price, 2))
            print(round(next_price, 2))
        data[f"Sim_{i}"] = prices
    
    sim_df = pd.DataFrame(data)
    return sim_df

if __name__ == "__main__":
    ticker_input = "AAPL"
    period_input = "1y"

    price_df = get_df(ticker_input)

    if BACK_TEST:
        train_data, test_data = split_df(price_df, x=100)
        last_price = round(float(train_data["Close"].iloc[-1]), 2)
    else:
        train_data = price_df
        last_price = round(float(train_data["Close"].iloc[-1]), 2)

    log_returns_df = compute_log_returns(train_data)
    anualized_mu = calc_anualized_mu(log_returns_df)
    anualized_sigma = calc_anualized_sigma(log_returns_df)

    sim_df = run_sim(anualized_mu, anualized_sigma, last_price, price_df)

    print(f"Day zero price {last_price}")
    print(f"last price: {round(float(test_data["Close"].iloc[-1]), 2)}, Expected price: {round(sim_df.iloc[-1].mean(),2)}")
    sim_df.plot(legend=False)

    # Plots Actual Price
    _ ,acutal_prices = split_df(price_df, x=100)
    acutal_prices["Close"].reset_index(drop=True)
    plt.plot(acutal_prices["Close"].reset_index(drop=True), color="black")

    plt.axhline(last_price, linestyle="--", color="Black", label=f"Last Price: ${last_price}")
    plt.axhline(round(sim_df.iloc[-1].mean(),2), linestyle=":", color="Black")

    plt.title(f"{ticker_input} GBM Simulations ({100}  days)")
    plt.xlabel("Day")
    plt.ylabel("Price")
    plt.show()