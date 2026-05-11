import os
import requests
import psycopg2
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

API_KEY = os.getenv('AIRNOW_API_KEY')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

ZIPCODE = '84078'
DISTANCE = 25
START_DATE = datetime(2026, 5, 2, 15, tzinfo=timezone.utc)
END_DATE = datetime(2026, 5, 10, 15, tzinfo=timezone.utc)

def backfill():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    inserted = 0
    current = START_DATE

    while current <= END_DATE:
        date_str = current.strftime('%Y-%m-%dT%H-0000')
        url = (
            f"https://www.airnowapi.org/aq/observation/zipCode/historical/"
            f"?format=application/json&zipCode={ZIPCODE}"
            f"&date={date_str}&distance={DISTANCE}&API_KEY={API_KEY}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            for obs in response.json():
                cur.execute("""
                    INSERT INTO observations
                        (recorded_at, parameter, aqi, category, latitude, longitude, reporting_area, state_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    current,
                    obs.get('ParameterName'),
                    obs.get('AQI'),
                    obs.get('Category', {}).get('Name'),
                    obs.get('Latitude'),
                    obs.get('Longitude'),
                    obs.get('ReportingArea'),
                    obs.get('StateCode'),
                ))
                inserted += 1
        current += timedelta(days=1)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Backfilled {inserted} AQI records from {START_DATE.date()} to {END_DATE.date()}")

if __name__ == '__main__':
    backfill()
