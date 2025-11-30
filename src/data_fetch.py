# src/data_fetch.py
import pandas as pd
import yfinance as yf
import datetime as dt

def fetch_stock(ticker, start, end):
    """Return daily adj close DataFrame for ticker."""
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    # keep Adjusted Close as 'Adj Close' or use 'Close' if auto_adjust True
    if 'Close' in df.columns:
        out = df['Close'].to_frame(name=ticker)
    else:
        out = df['Adj Close'].to_frame(name=ticker)
    out.index = pd.to_datetime(out.index)
    return out


def fetch_wilshire_and_gdp(start, end):
    """
    Try to fetch Wilshire market cap (WILL5000INDFC) and GDP (GDP) from FRED and return a DataFrame
    with a Buffett ratio (marketcap / GDP). If that fails, raise an Exception and caller can fallback.
    """
    # series ids may change; handle exceptions
    # WILL5000INDFC = Wilshire 5000 Total Market Full Cap (try)
    try:
        wil = DataReader('WILL5000INDFC', 'fred', start, end)   # total market cap series
        gdp = DataReader('GDP', 'fred', start, end)             # GDP (billions of $) — FRED units
        # Align frequencies: will likely be daily / monthly; GDP is quarterly. Convert both to quarterly
        wil_q = wil.resample('Q').last()
        # If will is index rather than dollar value, make sure units are comparable — user check encouraged.
        ratio = (wil_q['WILL5000INDFC'] / gdp['GDP']).rename('buffett_ratio')
        ratio = ratio.to_frame()
        return ratio
    except Exception as e:
        raise

def fetch_buffett_fallback(start, end):
    """
    Fallback: fetch FRED series that directly gives Stock Market Cap to GDP ratio if available.
    Example series ID: 'DDDM01USA156NWDB' (Stock Market Capitalization to GDP for United States).
    This series may be annual; check frequency and resample as needed.
    """
    try:
        series = DataReader('DDDM01USA156NWDB', 'fred', start, end)
        series.columns = ['buffett_ratio_percent']
        # convert percent to ratio
        series['buffett_ratio'] = series['buffett_ratio_percent'] / 100.0
        return series[['buffett_ratio']]
    except Exception as e:
        # if even this fails, return None (app will handle)
        return None

# src/data_fetch.py
import pandas as pd
import yfinance as yf
from pandas_datareader.data import DataReader
import datetime as dt

def fetch_stock(ticker, start, end):
    """Return daily adj close DataFrame for ticker."""
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    # keep Adjusted Close as 'Adj Close' or use 'Close' if auto_adjust True
    if 'Close' in df.columns:
        out = df[['Close']].rename(columns={'Close': ticker})

    else:
        out = df['Adj Close'].rename(ticker).to_frame()
    out.index = pd.to_datetime(out.index)
    return out

def fetch_wilshire_and_gdp(start, end):
    """
    Try to fetch Wilshire market cap (WILL5000INDFC) and GDP (GDP) from FRED and return a DataFrame
    with a Buffett ratio (marketcap / GDP). If that fails, raise an Exception and caller can fallback.
    """
    # series ids may change; handle exceptions
    # WILL5000INDFC = Wilshire 5000 Total Market Full Cap (try)
    try:
        wil = DataReader('WILL5000INDFC', 'fred', start, end)   # total market cap series
        gdp = DataReader('GDP', 'fred', start, end)             # GDP (billions of $) — FRED units
        # Align frequencies: will likely be daily / monthly; GDP is quarterly. Convert both to quarterly
        wil_q = wil.resample('Q').last()
        # If will is index rather than dollar value, make sure units are comparable — user check encouraged.
        ratio = (wil_q['WILL5000INDFC'] / gdp['GDP']).rename('buffett_ratio')
        ratio = ratio.to_frame()
        return ratio
    except Exception as e:
        raise

def fetch_buffett_fallback(start, end):
    """
    Fallback: fetch FRED series that directly gives Stock Market Cap to GDP ratio if available.
    Example series ID: 'DDDM01USA156NWDB' (Stock Market Capitalization to GDP for United States).
    This series may be annual; check frequency and resample as needed.
    """
    try:
        series = DataReader('DDDM01USA156NWDB', 'fred', start, end)
        series.columns = ['buffett_ratio_percent']
        # convert percent to ratio
        series['buffett_ratio'] = series['buffett_ratio_percent'] / 100.0
        return series[['buffett_ratio']]
    except Exception as e:
        # if even this fails, return None (app will handle)
        return None

