"""
model.py
--------
Core Machine Learning logic for the Stock Price Prediction project.

Pipeline (matches the project synopsis):
1. Data Collection   -> fetch historical OHLCV data with yfinance
2. Data Preprocessing -> clean data, handle missing values, reset index
3. Feature Selection  -> use a simple time-index feature ("day number")
                         and the Close price as the target
4. Model Building     -> Linear Regression (scikit-learn)
5. Training           -> fit on historical data
6. Testing/Prediction -> forecast the next N days
7. Visualization      -> data is returned as JSON; charting happens
                         on the frontend (Chart.js)
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Step 1: Data Collection - download historical stock data."""
    data = yf.download(ticker, period=period, progress=False)
    if data.empty:
        raise ValueError(f"No data found for ticker '{ticker}'. Check the symbol and try again.")
    return data


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """Step 2: Data Preprocessing - clean data & handle missing values."""
    data = data.copy()
    data.dropna(inplace=True)
    data.reset_index(inplace=True)
    # Flatten MultiIndex columns (yfinance sometimes returns them for single tickers)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] if c[1] == "" else c[0] for c in data.columns]
    return data


def build_features(data: pd.DataFrame):
    """Step 3: Feature Selection - day index as feature, Close as target."""
    data["DayIndex"] = np.arange(len(data))
    X = data[["DayIndex"]].values
    y = data["Close"].values
    return X, y, data


def train_model(X, y):
    """Step 4 & 5: Model Building + Training (Linear Regression)."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False  # keep chronological order for time series
    )
    model = LinearRegression()
    model.fit(X_train, y_train)

    # basic evaluation on the held-out (most recent) slice
    y_pred_test = model.predict(X_test)
    metrics = {
        "mae": round(float(mean_absolute_error(y_test, y_pred_test)), 4),
        "r2_score": round(float(r2_score(y_test, y_pred_test)), 4),
    }
    return model, metrics


def predict_future(model: LinearRegression, data: pd.DataFrame, days: int):
    """Step 6: Testing & Prediction - forecast the next `days` closing prices."""
    last_index = int(data["DayIndex"].iloc[-1])
    future_indices = np.arange(last_index + 1, last_index + 1 + days).reshape(-1, 1)
    future_prices = model.predict(future_indices)

    last_date = pd.to_datetime(data["Date"].iloc[-1])
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=days)

    return future_dates, future_prices


def run_pipeline(ticker: str, days: int = 30, period: str = "1y"):
    """Runs the full end-to-end pipeline and returns a JSON-ready dict."""
    raw = fetch_stock_data(ticker, period)
    data = preprocess_data(raw)
    X, y, data = build_features(data)
    model, metrics = train_model(X, y)
    future_dates, future_prices = predict_future(model, data, days)

    result = {
        "ticker": ticker.upper(),
        "history": {
            "dates": data["Date"].dt.strftime("%Y-%m-%d").tolist(),
            "prices": [round(float(p), 2) for p in data["Close"].tolist()],
        },
        "prediction": {
            "dates": [d.strftime("%Y-%m-%d") for d in future_dates],
            "prices": [round(float(p), 2) for p in future_prices],
        },
        "metrics": metrics,
        "last_close": round(float(data["Close"].iloc[-1]), 2),
        "predicted_next_close": round(float(future_prices[0]), 2),
    }
    return result
