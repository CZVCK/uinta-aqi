# Uinta Basin Air Quality Monitor

Real-time AQI monitoring dashboard for Vernal, Utah and the Uinta Basin.

## Live
[air.czvck.com](http://air.czvck.com)

## Stack
- **Python** — data collection via EPA AirNow API
- **PostgreSQL** — time-series observation storage
- **Flask** — REST API serving `/api/aqi/current` and `/api/aqi/history`
- **nginx** — reverse proxy
- **Plotly.js** — interactive AQI trend charts
- **AWS EC2** — self-hosted on t3.micro Ubuntu instance
- **Cloudflare** — DNS and proxying

## How it works
A cron job runs `collect/fetch_aqi.py` every hour, pulling current AQI readings for PM2.5 and Ozone from the EPA AirNow API and storing them in PostgreSQL. A Flask API serves the data to a Plotly.js dashboard at `air.czvck.com`.

## Project structure

```uinta-aqi/
├── collect/fetch_aqi.py    # EPA AirNow API ingestion
├── api/app.py              # Flask REST API
├── dashboard/index.html    # Plotly.js frontend
├── db/schema.sql           # PostgreSQL schema
└── config/                 # Environment config (not committed)
```
## Local setup
```
bash
python3 -m venv venv && source venv/bin/activate
pip install flask psycopg2-binary requests python-dotenv
cp config/.env.example config/.env  # add your API key and DB credentials
python api/app.py
```
