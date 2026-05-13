import os
import psycopg2
from flask import Flask, jsonify
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

app = Flask(__name__)

PARAM_NORMALIZE = {
    'ozone': 'O3',
    'OZONE': 'O3',
    'Ozone': 'O3',
    'pm2.5': 'PM2.5',
    'pm10':  'PM10',
}

def normalize_param(name):
    return PARAM_NORMALIZE.get(name, name)

def get_db():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

@app.route('/api/aqi/current')
def current():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (parameter)
            parameter, aqi, category, recorded_at, reporting_area
        FROM observations
        ORDER BY parameter, recorded_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        'parameter': normalize_param(r[0]),
        'aqi': r[1],
        'category': r[2],
        'recorded_at': r[3].isoformat(),
        'reporting_area': r[4]
    } for r in rows])

@app.route('/api/aqi/history')
def history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT parameter, aqi, category, recorded_at
        FROM observations
        WHERE recorded_at >= NOW() - INTERVAL '7 days'
        ORDER BY recorded_at ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        'parameter': normalize_param(r[0]),
        'aqi': r[1],
        'category': r[2],
        'recorded_at': r[3].isoformat()
    } for r in rows])

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/weather/current')
def weather_current():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT temperature_f, temperature_c, wind_speed, humidity, recorded_at
        FROM weather
        ORDER BY recorded_at DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({'error': 'No weather data available'}), 404
    return jsonify({
        'temperature_f': float(row[0]),
        'temperature_c': float(row[1]),
        'wind_speed':    float(row[2]),
        'humidity':      row[3],
        'recorded_at':   row[4].isoformat()
    })

@app.route('/api/weather/history')
def weather_history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT temperature_f, temperature_c, wind_speed, humidity, recorded_at
        FROM weather
        WHERE recorded_at >= NOW() - INTERVAL '7 days'
        ORDER BY recorded_at ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        'temperature_f': float(r[0]),
        'temperature_c': float(r[1]),
        'wind_speed':    float(r[2]),
        'humidity':      r[3],
        'recorded_at':   r[4].isoformat()
    } for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
