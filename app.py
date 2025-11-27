
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

from src.data_fetch import fetch_stock, fetch_wilshire_and_gdp, fetch_buffett_fallback
from src.analysis import compute_log_trend, compute_smooth_trend, pct_distance

st.set_page_config(layout='wide', page_title='Simple Indicator: Price vs Ideal + Buffett')

st.title("Simple Indicator: Price vs Ideal Trajectory (+ Buffett Indicator)")

# Sidebar controls
with st.sidebar:
    st.header("Inputs")
    ticker = st.text_input("Ticker (e.g., AAPL)", value="AAPL").upper()
    end_date = st.date_input("End date", date.today())
    start_date = st.date_input("Start date", end_date - timedelta(days=365*3))
    trend_type = st.selectbox("Ideal trajectory method", ["CAGR (log-linear)", "Smoothed log trend"])
    smooth_window = st.slider("Smoothing window (days, for smoothed method)", 5, 251, 63)

st.info("Note: Buffett indicator is market-cap / GDP. App will try to fetch Wilshire+GDP from FRED; if not available it will fall back to a precomputed ratio.")

# -- fetch data
@st.cache_data(ttl=3600)
def get_data(ticker, start, end):
    stock = fetch_stock(ticker, start, end)
    # attempt Wilshire + GDP -> buffett ratio
    try:
        buffett = fetch_wilshire_and_gdp(start, end)
    except Exception:
        buffett = fetch_buffett_fallback(start, end)
    return stock, buffett

stock_df, buffett_df = get_data(ticker, start_date, end_date)

if stock_df is None or stock_df.empty:
    st.error("No price data found for ticker. Try another ticker or broaden the date range.")
    st.stop()

# compute ideal
price_series = stock_df.iloc[:,0].rename('price')
if trend_type == "CAGR (log-linear)":
    ideal = compute_log_trend(price_series)
else:
    ideal = compute_smooth_trend(price_series, window_days=smooth_window, polyorder=2)

dist_pct = pct_distance(price_series.reindex(ideal.index), ideal).iloc[-1]

# Main plot (price + ideal)
fig = go.Figure()
fig.add_trace(go.Scatter(x=price_series.index, y=price_series.values, mode='lines', name=f'{ticker} price'))
fig.add_trace(go.Scatter(x=ideal.index, y=ideal.values, mode='lines', name='Ideal trajectory', line=dict(dash='dash')))
fig.update_layout(title=f"{ticker} — actual vs ideal (last {len(price_series)} days)", yaxis_title='Price (USD)', xaxis_title='Date', height=500)

# Buffett panel: if available plot it
if buffett_df is not None and not buffett_df.empty:
    # align and resample to monthly for plotting
    buffett_plot = buffett_df.dropna()
    # show latest value and historical median
    buffett_latest = buffett_plot['buffett_ratio'].iloc[-1]
    buffett_median = buffett_plot['buffett_ratio'].median()
    buffett_pct = buffett_latest * 100.0
    st.metric("Buffett indicator (market cap / GDP)", f"{buffett_pct:.1f}%")
    # subplot display
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=buffett_plot.index, y=buffett_plot['buffett_ratio']*100, mode='lines', name='Buffett % (MarketCap/GDP)'))
    fig2.add_trace(go.Scatter(x=buffett_plot.index, y=[buffett_median*100]*len(buffett_plot), mode='lines', name='Historical median', line=dict(dash='dash')))
    fig2.update_layout(title='Buffett indicator (market cap / GDP)', yaxis_title='Percentage (%)', xaxis_title='Date', height=300)
else:
    fig2 = None

# Layout
col1, col2 = st.columns([3,1])
with col1:
    st.plotly_chart(fig, use_container_width=True)
    if fig2 is not None:
        st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.subheader("Summary")
    st.write(f"Ticker: **{ticker}**")
    st.write(f"Latest price: **${price_series.iloc[-1]:.2f}**")
    st.write(f"CAGR trend price (start -> last fitted): **${ideal.iloc[-1]:.2f}**")
    st.write(f"Distance from ideal: **{dist_pct:.2f}%** (positive = price above ideal)")
    if buffett_df is not None and not buffett_df.empty:
        st.write(f"Buffett latest: **{buffett_pct:.1f}%**; historical median: **{buffett_median*100:.1f}%**")
        # color guidance
        if buffett_latest < buffett_median*0.9:
            st.success("Market appears relatively cheap vs. history.")
        elif buffett_latest > buffett_median*1.1:
            st.warning("Market appears relatively expensive vs. history.")
        else:
            st.info("Market near historical median valuation.")
    else:
        st.write("Buffett indicator: not available (FRED fallback failed).")

st.caption("Method: Ideal trajectory is a statistical trend, not a fundamental price target. Use for illustration only.")

