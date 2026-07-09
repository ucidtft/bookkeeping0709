import os, json, sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "analytics.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                device_id TEXT PRIMARY KEY,
                first_launch TEXT,
                last_launch TEXT,
                version TEXT,
                launch_count INTEGER DEFAULT 1,
                model TEXT
            )
        """)
        g.db.commit()
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop("db", None)
    if db: db.close()

@app.route("/ping", methods=["POST"])
def ping():
    data = request.json
    device_id = data.get("device_id", "unknown")
    version = data.get("version", "unknown")
    model = data.get("model", "unknown")
    now = datetime.now().isoformat()
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE device_id = ?", (device_id,)).fetchone()
    if row:
        db.execute("UPDATE users SET last_launch=?, version=?, launch_count=launch_count+1, model=? WHERE device_id=?", 
                   (now, version, model, device_id))
    else:
        db.execute("INSERT INTO users (device_id, first_launch, last_launch, version, launch_count, model) VALUES (?,?,?,?,1,?)",
                   (device_id, now, now, version, model))
    db.commit()
    total = db.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    return jsonify({"ok": True, "total_users": total})

@app.route("/stats")
def stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    today = datetime.now().strftime("%Y-%m-%d")
    today_active = db.execute("SELECT COUNT(*) as c FROM users WHERE last_launch LIKE ?", (today + "%",)).fetchone()["c"]
    users = db.execute("SELECT * FROM users ORDER BY last_launch DESC").fetchall()
    return jsonify({
        "total_users": total,
        "today_active": today_active,
        "users": [dict(u) for u in users]
    })

@app.route("/")
def index():
    return "<h1>AccountBook Analytics</h1><a href=/stats>View Stats</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
