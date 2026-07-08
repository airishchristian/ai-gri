# Ai-gri

A web dashboard for Filipino farmers with field management, live 5-day
weather forecasts (Open-Meteo), market prices, and AI crop disease
detection powered by Claude's vision capabilities.

## How to run

1. `pip install -r requirements.txt`
2. Add your Anthropic API key to `.streamlit/secrets.toml`:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
3. `streamlit run main.py`
4. App opens at http://localhost:8501

## Weather

Open-Meteo is completely free and requires no API key. Weather is
fetched live using the latitude/longitude saved on each field. If a
field has no coordinates (0.0, 0.0), weather won't show for that
field — add coordinates when creating or editing a field (tip: right
click your farm location on Google Maps to copy the coordinates).

## Deploy free on Streamlit Community Cloud

1. Push this code to GitHub (secrets.toml is gitignored — don't commit it)
2. Go to share.streamlit.io
3. Connect your repo, set main file = `main.py`
4. Add `ANTHROPIC_API_KEY` under the app's Secrets settings
5. Click Deploy — live URL in ~2 minutes

## Market prices

Market prices come from `market_prices.py`, which reads
`market_prices.csv` in the project root using pandas — that CSV is
the only data source, no remote URL or built-in fallback.

The CSV is a **tidy time series** — one row per commodity per date —
so the same file powers both the metric cards and the trend chart on
the dashboard:
```
date,commodity,price,unit
2021-01-01,Palay (dry),18.50,kg
2021-02-01,Palay (dry),18.70,kg
```
`date` accepts `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` — monthly or annual
data both work. There's no `change` column: the % change shown on
each metric card is computed automatically from the latest two data
points for that commodity, whatever the granularity.

Prices/trends are cached for 1 hour so the dashboard doesn't re-read
the CSV on every click; there's a "Refresh prices" button on the
dashboard to force an immediate reload. The dashboard also has a
commodity dropdown under "Price Trend" that plots the full history
for whichever commodity you pick, using `st.line_chart`.

The `market_prices.csv` shipped in this repo is **synthetic sample
data only** — not real PSA figures. Replace it with real data
(reshaped into the format above) before using it to make actual
farming decisions.

## Note on storage

`farmers.db` is a local SQLite file and will reset whenever Streamlit
Cloud restarts your app. For persistent storage in production, swap
SQLite for a hosted database (e.g. Supabase) by replacing the
`sqlite3` calls in `db.py` with the Supabase client, and storing
`SUPABASE_URL` / `SUPABASE_KEY` in secrets.toml.
