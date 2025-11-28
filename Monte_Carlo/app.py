import streamlit as st
import matplotlib.pyplot as plt 
import plotly.express as px
import yfinance as yf
import altair as alt

from main import get_df, split_df, run_sim


#ticker = "AAPL"
#period = "1y"

st.title("Monte Carlo Simulation")
ticker = st.text_input("Enter a Ticker: ")

SIM_DAYS = int(st.number_input("Ammount of Days to Sim: "))

BACK_TEST = st.toggle("Activate Back test")

if BACK_TEST:
    BACK_TEST_DAYS_AMMOUNT = st.number_input("Ammount of Days: ") 

if ticker and SIM_DAYS:
    price_df = get_df(ticker)

    train_data, test_data = split_df(price_df, x=100)

    st.write(ticker)

    fig = px.line(
        test_data,
        x=test_data.index,
        y="Close",
        title=f"{ticker} - Simulated Returns Over {SIM_DAYS} Trading Days"
    )
    fig.update_layout(
        xaxis_title = "Days Simulated"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("Raw Data Preview")
    st.dataframe(price_df)
