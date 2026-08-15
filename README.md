# Stock Price Prediction using Machine Learning

A full-stack version of the project synopsis: a Python/Flask **backend** that
runs the ML pipeline (data collection → preprocessing → feature selection →
Linear Regression → prediction) and a plain HTML/CSS/JS **frontend** that
calls it and charts the results.

```
stock-prediction-project/
├── backend/
│   ├── app.py            Flask API (routes)
│   ├── model.py           ML pipeline (yfinance + scikit-learn)
│   └── requirements.txt
├── frontend/
│   ├── index.html         Page structure
│   ├── style.css           Styling
│   └── script.js           Calls the API, renders the chart
└── README.md
```

## 1. Run the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

You should see Flask start on **http://127.0.0.1:5000**. Confirm it's alive:

```bash
curl http://127.0.0.1:5000/api/health
# {"status": "ok", "message": "Stock Prediction API is running"}
```

Try a prediction directly:

```bash
curl "http://127.0.0.1:5000/api/predict?ticker=AAPL&days=30&period=1y"
```

## 2. Run the frontend

The frontend is static HTML/CSS/JS — no build step needed. Open
`frontend/index.html` in one of two ways:

- **Double-click it** to open directly in a browser, or
- **Serve it** (recommended, avoids some browser file:// restrictions):
  ```bash
  cd frontend
  python -m http.server 5500
  # then visit http://127.0.0.1:5500
  ```

## 3. How the two sides connect

This is the important part — the frontend and backend are two separate
programs that talk over HTTP:

1. **`frontend/script.js`** defines:
   ```js
   const API_BASE_URL = "http://127.0.0.1:5000";
   ```
   This must point at wherever your Flask server is actually running. If you
   deploy the backend elsewhere (e.g. Render, Railway, a VM), update this to
   that URL, e.g. `https://your-api.onrender.com`.

2. When you click **Predict**, `script.js` calls:
   ```js
   fetch(`${API_BASE_URL}/api/predict?ticker=AAPL&period=1y&days=30`)
   ```
   This is a plain `GET` request with query parameters — no framework needed
   on the frontend.

3. **CORS**: browsers block a page on one origin (e.g.
   `http://127.0.0.1:5500`) from calling an API on another origin (e.g.
   `http://127.0.0.1:5000`) unless the server explicitly allows it. That's
   why `backend/app.py` has:
   ```python
   from flask_cors import CORS
   CORS(app)
   ```
   `CORS(app)` adds the `Access-Control-Allow-Origin` header to every
   response so the browser permits the frontend to read it. Without this
   line, the fetch call in `script.js` would fail with a CORS error in the
   browser console even though the backend is running fine.

4. **Flask returns JSON**, `script.js` reads it and hands it to Chart.js:
   ```json
   {
     "ticker": "AAPL",
     "history": { "dates": [...], "prices": [...] },
     "prediction": { "dates": [...], "prices": [...] },
     "metrics": { "mae": 3.21, "r2_score": 0.87 },
     "last_close": 214.32,
     "predicted_next_close": 216.05
   }
   ```
   The frontend never touches yfinance, pandas, or scikit-learn directly —
   it only ever sees this JSON contract. That separation is the whole point
   of a frontend/backend split: you could swap Linear Regression for a
   different model, or swap yfinance for another data source, and the
   frontend would not need to change at all as long as the JSON shape stays
   the same.

## 4. API reference

| Method | Endpoint        | Query params                          | Description                       |
|--------|-----------------|----------------------------------------|------------------------------------|
| GET    | `/api/health`   | —                                      | Health check                       |
| GET    | `/api/predict`  | `ticker` (required), `days` (default 30), `period` (default `1y`) | Runs the full ML pipeline and returns history + forecast |

## 5. Notes & next steps

- Tickers use Yahoo Finance symbols (e.g. `AAPL`, `TSLA`, `INFY.NS` for NSE-listed stocks).
- The model is intentionally simple (`Close price ~ day index`), matching
  the synopsis's use of Linear Regression — it captures trend, not
  volatility, news, or fundamentals. Good next steps: add more features
  (volume, moving averages), try `RandomForestRegressor` or an LSTM, and
  add authentication/rate limiting before deploying publicly.
- If `python app.py` errors on `yfinance`, make sure your machine has
  internet access — it fetches live data from Yahoo Finance at request time.
