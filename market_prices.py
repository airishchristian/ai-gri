"""
market_prices.py
Loads market price history for the dashboard from market_prices.csv
and derives current prices, % change, and full trend lines from it.

The CSV is the single source of truth — synthetic sample data, not
real PSA figures. Replace it with real data (same format) if needed.

CSV format (long/tidy shape — one row per commodity per date):
    date,commodity,price,unit
    2021-01-01,Palay (dry),18.50,kg
    2021-02-01,Palay (dry),18.70,kg
    2021-01-01,Corn (dry),16.20,kg
    ...

"date" accepts YYYY-MM-DD, YYYY-MM, or YYYY (monthly or annual data
both work — the chart just plots whatever points exist). "change"
is not a CSV column: it's computed automatically as the percent
difference between the latest two data points for each commodity.
"""

import pandas as pd
import streamlit as st

LOCAL_CSV_PATH = "market_prices.csv"


def _parse_history(df: pd.DataFrame) -> dict:
    """
    Turns a raw (date, commodity, price, unit) DataFrame into:
        {commodity: [(date, price, unit), ...]}  sorted ascending by date
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["commodity"] = df["commodity"].astype(str).str.strip()
    df["unit"] = df["unit"].astype(str).str.strip()
    df = df.dropna(subset=["date", "price", "commodity"])
    df = df.sort_values("date")

    history = {}
    for name, group in df.groupby("commodity"):
        history[name] = list(
            zip(group["date"].dt.date, group["price"], group["unit"])
        )
    return history


@st.cache_data(ttl=3600, show_spinner=False)
def _load_history_cached():
    """
    Cached for 1 hour so the dashboard doesn't re-read the CSV on
    every rerun or widget interaction. Returns
    (history dict, fetched_at datetime).
    history shape: {commodity: [(date, price, unit), ...]} ascending.
    """
    df = pd.read_csv(LOCAL_CSV_PATH)
    return _parse_history(df), pd.Timestamp.now()


def get_market_prices():
    """
    Public entry point for the metric cards.
    Returns (prices dict, fetched_at datetime) where
    prices = {commodity: {"price":.., "unit":.., "change":..}} using
    the latest data point and % change vs the previous data point.
    """
    history, fetched_at = _load_history_cached()
    prices = {}
    for name, points in history.items():
        if not points:
            continue
        _, latest_price, unit = points[-1]
        if len(points) >= 2:
            prev_price = points[-2][1]
            change = ((latest_price - prev_price) / prev_price * 100) if prev_price else 0.0
        else:
            change = 0.0
        prices[name] = {"price": latest_price, "unit": unit, "change": change}
    return prices, fetched_at


def get_price_trend(commodity: str):
    """
    Returns [(date, price), ...] ascending for one commodity, for
    charting. Empty list if the commodity isn't in the data.
    """
    history, _ = _load_history_cached()
    points = history.get(commodity, [])
    return [(d, p) for d, p, _ in points]


def get_commodity_list():
    """Returns the list of commodity names currently available."""
    history, _ = _load_history_cached()
    return list(history.keys())


def refresh_market_prices():
    """Call from a 'Refresh prices' button to bust the 1-hour cache."""
    _load_history_cached.clear()
