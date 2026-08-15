/**
 * script.js
 * ---------
 * This is the piece that CONNECTS the frontend to the backend.
 *
 * It calls the Flask API (see ../backend/app.py) at API_BASE_URL,
 * gets back JSON, and renders it with Chart.js.
 */

// ⚙️ CONNECTION POINT: this must match where your Flask backend is running.
// Default Flask dev server -> http://127.0.0.1:5000
const API_BASE_URL = "http://127.0.0.1:5000";

const form = document.getElementById("predict-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const btn = document.getElementById("predict-btn");

let chart; // holds the Chart.js instance so we can destroy/redraw it

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const ticker = document.getElementById("ticker").value.trim().toUpperCase();
  const period = document.getElementById("period").value;
  const days = document.getElementById("days").value;

  if (!ticker) return;

  setLoading(true);
  setStatus(`Fetching data and training model for ${ticker}…`, false);
  resultsEl.classList.add("hidden");

  try {
    const url = `${API_BASE_URL}/api/predict?ticker=${encodeURIComponent(ticker)}&period=${period}&days=${days}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    renderResults(data);
    setStatus(`Model trained on ${data.history.dates.length} trading days of ${data.ticker}.`, false);
  } catch (err) {
    setStatus(
      `⚠ ${err.message}. Make sure the backend is running at ${API_BASE_URL} (see README).`,
      true
    );
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  btn.disabled = isLoading;
  btn.textContent = isLoading ? "Predicting…" : "Predict";
}

function setStatus(message, isError) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", !!isError);
}

function renderResults(data) {
  resultsEl.classList.remove("hidden");

  document.getElementById("last-close").textContent = `$${data.last_close}`;
  document.getElementById("next-close").textContent = `$${data.predicted_next_close}`;
  document.getElementById("r2-score").textContent = data.metrics.r2_score;
  document.getElementById("mae").textContent = `$${data.metrics.mae}`;
  document.getElementById("chart-title").textContent = `${data.ticker} · Historical & Predicted Price`;

  const historyLabels = data.history.dates;
  const predictionLabels = data.prediction.dates;
  const allLabels = [...historyLabels, ...predictionLabels];

  // Pad the prediction series with nulls for the historical range so both
  // datasets line up on the same x-axis, and connect them at the seam.
  const historyData = [...data.history.prices, ...Array(predictionLabels.length).fill(null)];
  const predictionData = [
    ...Array(historyLabels.length - 1).fill(null),
    data.history.prices[data.history.prices.length - 1],
    ...data.prediction.prices,
  ];

  const ctx = document.getElementById("price-chart").getContext("2d");
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: allLabels,
      datasets: [
        {
          label: "Historical",
          data: historyData,
          borderColor: "#6C9BFF",
          backgroundColor: "rgba(108,155,255,0.08)",
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.15,
          fill: true,
        },
        {
          label: "Predicted",
          data: predictionData,
          borderColor: "#E8B44C",
          borderDash: [6, 4],
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.15,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { color: "#7C8797", maxTicksLimit: 10 },
          grid: { color: "#232A38" },
        },
        y: {
          ticks: { color: "#7C8797", callback: (v) => `$${v}` },
          grid: { color: "#232A38" },
        },
      },
    },
  });
}
