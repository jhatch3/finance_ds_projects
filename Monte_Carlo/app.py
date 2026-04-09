import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Monte Carlo Simulator", layout="wide")
st.title("Monte Carlo Price Simulation")
st.caption("Geometric Brownian Motion from historical yfinance data")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")

    PRESETS = {
        "Bitcoin (BTC)":  "BTC-USD",
        "Ethereum (ETH)": "ETH-USD",
        "Solana (SOL)":   "SOL-USD",
        "S&P 500 (SPY)":  "SPY",
        "Apple (AAPL)":   "AAPL",
        "Custom":         None,
    }
    preset = st.selectbox("Asset", list(PRESETS.keys()))
    if preset == "Custom":
        ticker_input = st.text_input("Ticker symbol", placeholder="e.g. TSLA")
    else:
        ticker_input = PRESETS[preset]
        st.caption(f"Ticker: `{ticker_input}`")

    period  = st.selectbox("Historical period", ["1y", "2y", "5y", "10y", "max"], index=2)
    horizon = st.slider("Forecast horizon (days)", 30, 730, 365)
    n_sims  = st.slider("Number of simulations", 100, 5000, 1000, step=100)
    ci      = st.slider("Confidence interval (%)", 80, 99, 95)

    st.divider()
    st.subheader("Market Scenario")

    SCENARIOS = {
        "Base (historical)": {"drift_scale": 1.0,  "vol_scale": 1.0,  "color": "#1A3A5C", "label": "Base"},
        "Bull market":       {"drift_scale": 2.0,  "vol_scale": 0.85, "color": "#1B5E20", "label": "Bull"},
        "Bear market":       {"drift_scale": -1.0, "vol_scale": 1.4,  "color": "#7A1E1E", "label": "Bear"},
        "High volatility":   {"drift_scale": 1.0,  "vol_scale": 2.0,  "color": "#4A148C", "label": "High Vol"},
        "Custom":            {"drift_scale": None, "vol_scale": None,  "color": "#555555", "label": "Custom"},
    }

    scenario = st.selectbox("Scenario", list(SCENARIOS.keys()))
    sc = SCENARIOS[scenario]

    if scenario == "Custom":
        drift_scale = st.slider("Drift multiplier", -3.0, 3.0, 1.0, step=0.1,
                                help="Scales the historical daily drift. Negative = bearish bias.")
        vol_scale   = st.slider("Volatility multiplier", 0.1, 3.0, 1.0, step=0.1,
                                help="Scales historical daily volatility.")
        sc = {**sc, "drift_scale": drift_scale, "vol_scale": vol_scale}
    else:
        st.caption(
            f"Drift ×{sc['drift_scale']}  |  Volatility ×{sc['vol_scale']}"
        )

    run = st.button("Run Simulation", type="primary", use_container_width=True)

# ── Style helpers ─────────────────────────────────────────────────────────────
NAVY  = "#1A3A5C"
RED   = "#7A1E1E"
SLATE = "#444444"
GRID  = "#DDDDDD"

def apply_style(ax):
    ax.set_facecolor("white")
    ax.grid(True, axis="y", color=GRID, linewidth=0.5, linestyle=":")
    sns.despine(ax=ax)
    ax.tick_params(colors=SLATE)
    ax.xaxis.label.set_color(SLATE)
    ax.yaxis.label.set_color(SLATE)
    ax.title.set_color(SLATE)

def dollar_fmt(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# ── Main logic ────────────────────────────────────────────────────────────────
if run:
    ticker = ticker_input.strip().upper() if ticker_input else None
    if not ticker:
        st.warning("Enter a ticker symbol.")
        st.stop()

    with st.spinner(f"Fetching {ticker} data..."):
        raw = yf.Ticker(ticker).history(period=period, interval="1d")

    if raw.empty:
        st.error(f"No data returned for **{ticker}**. Check the symbol and try again.")
        st.stop()

    raw.index = raw.index.tz_localize(None)
    price = raw["Close"].dropna()
    log_r = np.log(price / price.shift(1)).dropna()

    mu_daily    = log_r.mean()
    sigma_daily = log_r.std()
    S0          = price.iloc[-1]

    # Apply scenario scaling
    mu_sim    = mu_daily    * sc["drift_scale"]
    sigma_sim = sigma_daily * sc["vol_scale"]
    SIM_COLOR = sc["color"]

    # GBM simulation
    dt  = 1
    rng = np.random.default_rng(42)
    Z   = rng.standard_normal((horizon, n_sims))
    daily = np.exp((mu_sim - 0.5 * sigma_sim**2) * dt + sigma_sim * np.sqrt(dt) * Z)
    paths = np.vstack([np.ones(n_sims) * S0, daily])
    paths = np.cumprod(paths, axis=0)

    lo  = (100 - ci) / 2
    hi  = 100 - lo
    p_lo    = np.percentile(paths, lo,  axis=1)
    p_hi    = np.percentile(paths, hi,  axis=1)
    p_med   = np.percentile(paths, 50,  axis=1)
    p_mean  = paths.mean(axis=1)
    final   = paths[-1, :]

    days_ax = np.arange(horizon + 1)

    # ── Layout ────────────────────────────────────────────────────────────────
    st.subheader(f"{ticker} — {n_sims:,} simulations over {horizon} days  ·  {sc['label']} scenario")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price",   f"${S0:,.2f}")
    col2.metric("Median Final",    f"${np.median(final):,.2f}",
                f"{(np.median(final)/S0 - 1)*100:+.1f}%")
    col3.metric(f"{ci}% CI Low",   f"${p_lo[-1]:,.2f}",
                f"{(p_lo[-1]/S0 - 1)*100:+.1f}%")
    col4.metric(f"{ci}% CI High",  f"${p_hi[-1]:,.2f}",
                f"{(p_hi[-1]/S0 - 1)*100:+.1f}%")

    st.divider()

    # ── Fig 1: Simulation paths ───────────────────────────────────────────────
    fig1, ax1 = plt.subplots(figsize=(11, 4), facecolor="white")
    sample_idx = rng.choice(n_sims, size=min(300, n_sims), replace=False)
    for i in sample_idx:
        ax1.plot(days_ax, paths[:, i], color=SIM_COLOR, alpha=0.04, linewidth=0.5)
    ax1.fill_between(days_ax, p_lo, p_hi, color=SIM_COLOR, alpha=0.12,
                     label=f"{ci}% CI")
    ax1.plot(days_ax, p_med,  color=SIM_COLOR, linewidth=1.8, label="Median")
    ax1.plot(days_ax, p_mean, color=RED,   linewidth=1.2, linestyle="--", label="Mean")
    ax1.axhline(S0, color=SLATE, linewidth=0.8, linestyle=":", label="Current price")
    ax1.set_xlabel("Days forward", fontsize=9)
    ax1.set_ylabel("Price (USD)", fontsize=9)
    ax1.set_title(f"(a) Monte Carlo Simulation — {ticker}", loc="left",
                  fontsize=9, fontstyle="italic")
    dollar_fmt(ax1)
    ax1.legend(fontsize=8, frameon=False)
    apply_style(ax1)
    plt.tight_layout()
    st.pyplot(fig1, use_container_width=True)
    plt.close(fig1)

    # ── Fig 2 & 3 side by side ────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    # Final price distribution
    with c1:
        fig2, ax2 = plt.subplots(figsize=(6, 4), facecolor="white")
        sns.histplot(final, bins=80, stat="density", color=SIM_COLOR,
                     edgecolor="white", linewidth=0.3, alpha=0.7, ax=ax2, label="Simulated")
        mu_f, sig_f = final.mean(), final.std()
        xf = np.linspace(final.min(), final.max(), 300)
        ax2.plot(xf, stats.norm.pdf(xf, mu_f, sig_f), color=RED,
                 linewidth=1.4, linestyle="--", label="Normal fit")
        ax2.axvline(S0,       color="black", linewidth=1.0, linestyle=":", label="Current")
        ax2.axvline(p_lo[-1], color=SLATE,   linewidth=0.8, linestyle="--", alpha=0.7)
        ax2.axvline(p_hi[-1], color=SLATE,   linewidth=0.8, linestyle="--", alpha=0.7,
                    label=f"{ci}% CI bounds")
        ax2.set_xlabel("Final Price (USD)", fontsize=9)
        ax2.set_ylabel("Density", fontsize=9)
        ax2.set_title(f"(b) Final Price Distribution (day {horizon})",
                      loc="left", fontsize=9, fontstyle="italic")
        ax2.legend(fontsize=7, frameon=False)
        apply_style(ax2)
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)

    # Log return distribution of historical data
    with c2:
        fig3, ax3 = plt.subplots(figsize=(6, 4), facecolor="white")
        lr_pct = log_r * 100
        sns.histplot(lr_pct, bins=80, stat="density", color=SLATE,
                     edgecolor="white", linewidth=0.3, alpha=0.65, ax=ax3, label="Empirical")
        xl = np.linspace(lr_pct.min(), lr_pct.max(), 300)
        ax3.plot(xl, stats.norm.pdf(xl, lr_pct.mean(), lr_pct.std()),
                 color=RED, linewidth=1.4, linestyle="--", label="Normal fit")
        ax3.axvline(0, color=SLATE, linewidth=0.7, linestyle=":")
        ax3.set_xlabel("Log Return (%)", fontsize=9)
        ax3.set_ylabel("Density", fontsize=9)
        ax3.set_title("(c) Historical Log Return Distribution",
                      loc="left", fontsize=9, fontstyle="italic")
        ax3.legend(fontsize=7, frameon=False)
        skew_v = log_r.skew()
        kurt_v = log_r.kurt()
        ax3.text(0.98, 0.95,
                 f"μ = {lr_pct.mean():.3f}%\nσ = {lr_pct.std():.3f}%\n"
                 f"Skew = {skew_v:.3f}\nEx. Kurt = {kurt_v:.3f}",
                 transform=ax3.transAxes, ha="right", va="top", fontsize=8,
                 bbox=dict(boxstyle="square,pad=0.4", facecolor="white",
                           edgecolor="#AAAAAA", linewidth=0.6))
        apply_style(ax3)
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)
        plt.close(fig3)

    # ── Raw data expander ─────────────────────────────────────────────────────
    with st.expander("Historical price data"):
        st.dataframe(price.rename("Close").to_frame(), use_container_width=True)

else:
    st.info("Configure parameters in the sidebar and click **Run Simulation**.")
