"""
app.py
------
Flask backend for the Stock Price Prediction project.

This is the BACKEND. It exposes a small REST API that the
FRONTEND (in ../frontend) calls over HTTP to get predictions.

Run with:
    python app.py

The server starts on http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from model import run_pipeline

app = Flask(__name__)

# CORS lets the frontend (served from a different origin/port, e.g.
# http://127.0.0.1:5500 via Live Server, or opened as a local file)
# make requests to this API without the browser blocking them.
CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    """Simple endpoint the frontend can ping to confirm the backend is up."""
    return jsonify({"status": "ok", "message": "Stock Prediction API is running"})


@app.route("/api/predict", methods=["GET"])
def predict():
    """
    Main prediction endpoint.

    Query params:
        ticker : str  (required)  e.g. AAPL, MSFT, TSLA, INFY.NS
        days   : int  (optional, default 30) number of future days to predict
        period : str  (optional, default '1y') history window, e.g. 6mo, 1y, 5y

    Example:
        GET /api/predict?ticker=AAPL&days=30&period=1y
    """
    ticker = request.args.get("ticker", "").strip()
    days = request.args.get("days", default=30, type=int)
    period = request.args.get("period", default="1y", type=str)

    if not ticker:
        return jsonify({"error": "Please provide a 'ticker' query parameter, e.g. ?ticker=AAPL"}), 400
    if days <= 0 or days > 365:
        return jsonify({"error": "'days' must be between 1 and 365"}), 400

    try:
        result = run_pipeline(ticker, days=days, period=period)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Something went wrong: {exc}"}), 500


if __name__ == "__main__":
    # debug=True auto-reloads on code changes during development
    app.run(debug=True, port=5000)
