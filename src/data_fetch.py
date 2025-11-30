# src/data_fetch.py
import pandas as pd
import yfinance as yf
import requests

# -------------------------------------------
# 1. Fetch Stock Prices (yfinance only)
# -------------------------------------------
def fetch_stock(ticker, start, end):
    """
    Return daily adjusted close prices for a ticker.
    Compatible with Streamlit Cloud (no pandas_datareader).
    """
    df = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )

    # Prefer 'Close' because auto_adjust=True already adjusts it
    if "Close" in df.columns:
        out = df[["Close"]].rename(columns={"Close": ticker})
    else:
        out = df[["Adj Close"]].rename(columns={"Adj Close": ticker})

    out.index = pd.to_datetime(out.index)
    return out


# -------------------------------------------
# 2. Fetch Wilshire 5000 + GDP (via FRED JSON API)
# -------------------------------------------

FRED_API_KEY = ""  # Optional. Leaving blank still works with public series.

def _fred_request(series_id):
    """Internal helper to call FRED's JSON API safely."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if "observations" not in data:
        raise Exception(f"FRED: No observations returned for {series_id}")

    df = pd.DataFrame(data["observations"])
    df = df[df["value"] != "."].copy()
    df["value"] = pd.to_numeric(df["value"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")[["value"]]
    df.columns = [series_id]
    return df


def fetch_wilshire_and_gdp(start, end):
    """
    Compute Buffett Indicator = Wilshire 5000 Total Market Cap / US GDP.
    Uses FRED JSON API (Streamlit-safe).
    """
    try:
        wil = _fred_request("WILL5000INDFC")
        gdp = _fred_request("GDP")

        # Restrict to requested window
        wil = wil.loc[start:end]
        gdp = gdp.loc[start:end]

        # Align to quarterly
        wil_q = wil.resample("Q").last()
        gdp_q = gdp.resample("Q").last()

        ratio = (wil_q["WILL5000INDFC"] / gdp_q["GDP"]).rename("buffett_ratio")
        return ratio.to_frame()

    except Exception as e:
        print("Primary Wilshire + GDP fetch failed:", e)
        raise


# -------------------------------------------
# 3. Fallback — Stock Market Cap / GDP (%)
# -------------------------------------------

def fetch_buffett_fallback(start, end):
    """
    Fallback FRED series:
    'DDDM01USA156NWDB' = Stock Market Cap to GDP (percent).
    """
    try:
        df = _fred_request("DDDM01USA156NWDB")

        df = df.loc[start:end]
        df["buffett_ratio"] = df["DDDM01USA156NWDB"] / 100.0  # convert percent to ratio

        return df[["buffett_ratio"]]

    except Exception as e:
        print("Buffett fallback fetch failed:", e)
        return None
