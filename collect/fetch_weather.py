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

def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,wind_speed_10m,relative_humidity_2m"
        "&temperature_unit=fahrenheit"
        "&wind_speed_unit=mph"
        "&timezone=America/Denver"
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    current = data["current"]
    temp_f = current["temperature_2m"]
    wind_speed = current["wind_speed_10m"]
    humidity = current["relative_humidity_2m"]

    if any(v is None for v in (temp_f, wind_speed, humidity)):
        print("Skipping: Open-Meteo returned null for one or more fields")
        return

    temp_c = round((temp_f - 32) * 5 / 9, 2)
    recorded_at = datetime.now(timezone.utc)

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO weather (recorded_at, temperature_f, temperature_c, wind_speed, humidity)
        VALUES (%s, %s, %s, %s, %s)
    """, (recorded_at, temp_f, temp_c, wind_speed, humidity))
    conn.commit()
    cur.close()
    conn.close()

    print(f"Weather saved at {recorded_at}")
    print(f"Temp: {temp_f}°F / {temp_c}°C | Wind: {wind_speed} mph | Humidity: {humidity}%")

if __name__ == "__main__":
    fetch_weather()
