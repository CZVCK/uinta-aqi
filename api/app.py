import os
import psycopg2
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv('config/.env')

app = Flask(__name__)

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
        'parameter': r[0],
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
        ORDER BY recorded_at DESC
        LIMIT 200
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        'parameter': r[0],
        'aqi': r[1],
        'category': r[2],
        'recorded_at': r[3].isoformat()
    } for r in rows])

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
