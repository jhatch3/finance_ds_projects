import streamlit as st
import matplotlib.pyplot as plt 
import plotly.express as px
import yfinance as yf
import altair as alt
import numpy as np 

import streamlit as st
import matplotlib.pyplot as plt 
import plotly.express as px
import yfinance as yf
import altair as alt
import pandas as pd

def split_df(df, x: int):
    """
    Split df so the test set has exactly x rows.
    Train = all rows except last x.
    Test  = last x rows.
    """
    df = df.sort_index()

    test = df.iloc[-x:]     # last x rows
    train = df.iloc[:-x]    # everything before

    # Sanity check
    assert len(train) + len(test) == len(df), "train + test != total!"

    return train, test

def compute_log_returns(df):

    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index().set_index("Date")

    prices = df["Close"].astype(float)

    # Filter out non-positive prices to avoid log(<=0)
    prices = prices[prices > 0]

    log_returns = np.log(prices / prices.shift(1))
    log_returns = log_returns.dropna()

    # Make sure it's a Series
    if isinstance(log_returns, pd.DataFrame):
        log_returns = log_returns.iloc[:, 0]

    df["logReturns"] = log_returns
    df = df.dropna()
    return df 

from main import get_df, run_sim, calc_anualized_mu, calc_anualized_sigma


#ticker = "AAPL"
#period = "1y"

st.title("Monte Carlo Simulation")
ticker = st.text_input("Enter a Ticker: ")

SIM_DAYS = int(st.number_input("Ammount of Days to Simulations: "))
NUM_SIMS = int(st.number_input("Ammount of Simulations to Run: "))

# TODO: BACK TEST LOGIC
# BACK_TEST = st.toggle("Back Test")
# if BACK_TEST:
#     BACK_TEST_DAYS_AMMOUNT = st.number_input("Ammount of Days: ") 
# else:
#     BACK_TEST_DAYS_AMMOUNT = 0

if ticker and NUM_SIMS:
    # Get Data
    train_data = get_df(ticker)
    
    # TODO: BACK TEST LOGIC
    # if BACK_TEST:
    #     train_data, test_data = split_df(train_data, BACK_TEST_DAYS_AMMOUNT)
 

    # Calculate Need Statistics
    log_returns_df = compute_log_returns(train_data)
    anualized_mu = calc_anualized_mu(log_returns_df)
    anualized_sigma = calc_anualized_sigma(log_returns_df)


    # Run Simulation
    sim_df = run_sim(mu_annual=anualized_mu, sigma_annual=anualized_sigma, df=train_data, number_of_sims=NUM_SIMS, days=SIM_DAYS)

    sim_df_plot = sim_df.reset_index().rename(columns={"index": "Date"})

    if NUM_SIMS <= 5000: 
        fig = px.line(
            sim_df_plot,
            x="Date",
            y=sim_df_plot.columns[1:],  # all columns except Date
            title=f"{ticker} - Simulated Closing Prices Over {SIM_DAYS} Trading Days"
        )

        fig.update_layout(
            xaxis_title = "Days Simulated"
        )

        st.plotly_chart(fig, use_container_width=True)
    
    sim_mean = round(sim_df.iloc[-1].mean(),2)

    # Simulated Data Section
    st.header("Simulated Data Preview")
    final_day = sim_df.iloc[-1]
    sim_mean = final_day.mean()
    sim_std = final_day.std()

    lower = sim_mean - 1.96 * sim_std
    upper = sim_mean + 1.96 * sim_std

    winners = (final_day > sim_mean).mean() * 100

    st.markdown(f"""
        
            - **Expected {ticker} Price After {SIM_DAYS} Trading Days:** \${sim_mean:.2f}
            - **95% Confidence Interval:** [\${lower:.2f}, \${upper:.2f}]
            - {winners}% of Simulations ended in the green
    """)


    bins = int(np.clip(np.sqrt(NUM_SIMS), 20, 120))

    fig_hist = px.histogram(
        x=final_day,
        nbins=bins,
        title=f"{ticker} - Distribution of Final Simulated Prices after {SIM_DAYS} Days"
    )

    fig_hist.update_layout(
        xaxis_title="Final Simulated Price",
        yaxis_title="Frequency"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    st.dataframe(sim_df)

    # Raw Data Section
    st.header("Raw Data Preview")

    
    st.dataframe(train_data)

