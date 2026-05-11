# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Air quality and weather monitoring dashboard for the Uinta Basin (Vernal, UT). Runs on AWS EC2 with cron jobs pulling data from EPA AirNow and Open-Meteo APIs into PostgreSQL, served via Flask, displayed in a single-page Plotly.js dashboard. Live at http://air.czvck.com.

## Environment Setup

No requirements.txt exists. Install dependencies manually:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install flask psycopg2-binary requests python-dotenv
```

Config lives in `config/.env` (git-ignored, must create manually):

```
AIRNOW_API_KEY=<key>
DB_NAME=<db>
DB_USER=<user>
DB_PASSWORD=<pass>
DB_HOST=<host>
DB_PORT=5432
```

## Running the Application

```bash
# Start the API server
python api/app.py

# Run data collectors manually
python collect/fetch_aqi.py
python collect/fetch_weather.py

# Backfill historical data (edit date range in script first)
python collect/backfill_aqi.py
python collect/backfill_weather.py
```

The API runs on port 5000. The dashboard (`dashboard/index.html`) is a static file served by nginx and calls the API directly.

## Architecture

**Data flow:** Cron → collect scripts → PostgreSQL → Flask API → dashboard

- `collect/fetch_aqi.py` — Hourly cron. Calls EPA AirNow API for zip 84078 (25-mile radius), writes to `observations` table.
- `collect/fetch_weather.py` — 4x daily cron. Calls Open-Meteo (no key needed) for coordinates 40.4555, -109.5287, writes to `weather` table.
- `api/app.py` — Flask app on port 5000. Five endpoints: `/api/aqi/current`, `/api/aqi/history`, `/api/weather/current`, `/api/weather/history`, `/api/health`.
- `dashboard/index.html` — Single self-contained HTML file. Plotly.js dual-axis chart (AQI lines + temperature bars), auto-refreshes every 10 minutes.
- `db/schema.sql` — Only the `observations` table DDL. The `weather` table exists in production but is **missing from this file**.

## Database Schema Gap

`db/schema.sql` is missing the `weather` table definition. The actual table used by the app:

```sql
CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    recorded_at TIMESTAMP,
    temperature_f NUMERIC,
    temperature_c NUMERIC,
    wind_speed NUMERIC,
    humidity INTEGER
);
```

If recreating the database from schema.sql, add this table manually.

## Cron Schedule (Production)

```
0 * * * *    python collect/fetch_aqi.py       # hourly AQI
0 */6 * * *  python collect/fetch_weather.py   # 4x daily weather
```

Scripts use `python-dotenv` to load `config/.env` relative to the script's own directory. When adding new cron jobs, ensure the working directory or dotenv path resolves correctly from the cron environment.
