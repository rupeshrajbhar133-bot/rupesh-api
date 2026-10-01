from flask import Flask, request, jsonify
import sqlite3
import os
import requests

app = Flask(__name__)

DB_NAME = "database.db"
# Agar R2/Direct Download Link hai toh yahan daalein (Optional Auto-downloader)
DB_DOWNLOAD_URL = os.environ.get("DB_DOWNLOAD_URL", "")

API_NAME = "Rupesh Official Search API"
DEVELOPER = "@urrr.rupsam__"

def ensure_database():
    """Download database on Render startup if not present"""
    if not os.path.exists(DB_NAME) and DB_DOWNLOAD_URL:
        print("Downloading database.db from cloud storage...")
        r = requests.get(DB_DOWNLOAD_URL, stream=True)
        with open(DB_NAME, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print("Database download complete!")

def get_db_connection():
    ensure_database()
    if not os.path.exists(DB_NAME):
        return None
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def home():
    db_status = "Available" if os.path.exists(DB_NAME) else "Not Found"
    return jsonify({
        "status": "online",
        "api_name": API_NAME,
        "developer": DEVELOPER,
        "db_status": db_status,
        "message": "API is running successfully!"
    })

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"status": False, "message": "Query parameter missing! Example: /search?query=9876543210"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": False, "error": "database.db missing on server"}), 404

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]

    results = []
    for tbl in tables:
        try:
            cursor.execute(f"PRAGMA table_info(`{tbl}`)")
            columns = [col['name'] for col in cursor.fetchall()]
            if not columns:
                continue

            where_conditions = " OR ".join([f"`{col}` LIKE ?" for col in columns])
            sql_query = f"SELECT * FROM `{tbl}` WHERE {where_conditions} LIMIT 10"
            params = [f"%{query}%"] * len(columns)

            cursor.execute(sql_query, params)
            rows = cursor.fetchall()

            for row in rows:
                item = dict(row)
                item['_table'] = tbl
                results.append(item)
        except Exception:
            continue

    conn.close()

    if not results:
        return jsonify({"status": False, "total": 0, "developer": DEVELOPER, "result": []}), 404

    return jsonify({"status": True, "total": len(results), "developer": DEVELOPER, "result": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
