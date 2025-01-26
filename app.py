import sqlite3
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)
DATABASE = 'url_shortener.db'

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_url TEXT NOT NULL UNIQUE,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_time TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_url TEXT NOT NULL,
                access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT NOT NULL,
                FOREIGN KEY (short_url) REFERENCES urls (short_url)
            )
        ''')
        conn.commit()

# Generate a short URL using MD5 hash
def generate_short_url(original_url):
    hash_object = hashlib.md5(original_url.encode())
    return hash_object.hexdigest()[:8]

# Validate URL format
def is_valid_url(url):
    return url.startswith(('http://', 'https://'))

# API to create a shortened URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')
    expiry_hours = data.get('expiry_hours', 24)

    if not original_url or not is_valid_url(original_url):
        return jsonify({'error': 'Invalid URL'}), 400

    short_url = generate_short_url(original_url)
    creation_time = datetime.now()
    expiry_time = creation_time + timedelta(hours=expiry_hours)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO urls (original_url, short_url, creation_time, expiry_time)
            VALUES (?, ?, ?, ?)
        ''', (original_url, short_url, creation_time, expiry_time))
        conn.commit()

    return jsonify({'short_url': f'https://short.ly/{short_url}'}), 201

# API to redirect to the original URL
@app.route('/<path:short_url>', methods=['GET'])
def redirect_to_original(short_url):
    # Strip the base URL prefix if present
    if short_url.startswith('short.ly/'):
        short_url = short_url.replace('short.ly/', '')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT original_url, expiry_time FROM urls WHERE short_url = ?
        ''', (short_url,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'URL not found'}), 404

        original_url, expiry_time = result

        # Parse expiry_time with fractional seconds
        try:
            expiry_time = datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # Fallback to parsing without fractional seconds
            expiry_time = datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S')

        if datetime.now() > expiry_time:
            return jsonify({'error': 'URL has expired'}), 410

        # Log the access
        ip_address = request.remote_addr
        cursor.execute('''
            INSERT INTO access_logs (short_url, ip_address) VALUES (?, ?)
        ''', (short_url, ip_address))
        conn.commit()

    return redirect(original_url, code=302)

# API to retrieve analytics for a shortened URL
@app.route('/analytics/<short_url>', methods=['GET'])
def get_analytics(short_url):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM access_logs WHERE short_url = ?
        ''', (short_url,))
        access_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT access_time, ip_address FROM access_logs WHERE short_url = ?
        ''', (short_url,))
        access_logs = cursor.fetchall()

    return jsonify({
        'short_url': short_url,
        'access_count': access_count,
        'access_logs': [{'timestamp': log[0], 'ip_address': log[1]} for log in access_logs]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)