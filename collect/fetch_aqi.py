import os
import requests
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

API_KEY = os.getenv('AIRNOW_API_KEY')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Vernal, UT zip code
ZIP_CODE = '84078'
DISTANCE = 25  # miles radius

def fetch_aqi():
    url = 'https://www.airnowapi.org/aq/observation/zipCode/current/'
    params = {
        'format': 'application/json',
        'zipCode': ZIP_CODE,
        'distance': DISTANCE,
        'API_KEY': API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def save_observations(observations):
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    for obs in observations:
        cur.execute("""
            INSERT INTO observations
                (recorded_at, parameter, aqi, category, latitude, longitude, reporting_area, state_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datetime.now(timezone.utc),
            obs.get('ParameterName'),
            obs.get('AQI'),
            obs.get('Category', {}).get('Name'),
            obs.get('Latitude'),
            obs.get('Longitude'),
            obs.get('ReportingArea'),
            obs.get('StateCode')
        ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Saved {len(observations)} observations at {datetime.now(timezone.utc)}")

if __name__ == '__main__':
    observations = fetch_aqi()
    if observations:
        save_observations(observations)
        for obs in observations:
            print(f"{obs.get('ParameterName')}: AQI {obs.get('AQI')} ({obs.get('Category', {}).get('Name')})")
    else:
        print("No observations returned.")


