import os
import requests
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

LAT = 40.4555
LON = -109.5287
START_DATE = '2026-05-01'
END_DATE = '2026-05-15'

def backfill():
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={START_DATE}&end_date={END_DATE}"
        "&hourly=temperature_2m,wind_speed_10m,relative_humidity_2m"
        "&temperature_unit=fahrenheit"
        "&wind_speed_unit=mph"
        "&timezone=UTC"
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    hourly = data['hourly']
    times = hourly['time']
    temps_f = hourly['temperature_2m']
    winds = hourly['wind_speed_10m']
    humidities = hourly['relative_humidity_2m']

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM weather WHERE recorded_at >= %s AND recorded_at < %s",
        (START_DATE, END_DATE + ' 23:59:59')
    )

    inserted = 0
    skipped = 0
    for i, t in enumerate(times):
        temp_f = temps_f[i]
        wind = winds[i]
        humidity = humidities[i]

        if any(v is None for v in (temp_f, wind, humidity)):
            skipped += 1
            continue

        recorded_at = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
        temp_c = round((temp_f - 32) * 5 / 9, 2)

        cur.execute("""
            INSERT INTO weather (recorded_at, temperature_f, temperature_c, wind_speed, humidity)
            VALUES (%s, %s, %s, %s, %s)
        """, (recorded_at, temp_f, temp_c, wind, humidity))
        inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Backfilled {inserted} hourly records from {START_DATE} to {END_DATE} ({skipped} skipped due to null values)")

if __name__ == '__main__':
    backfill()
