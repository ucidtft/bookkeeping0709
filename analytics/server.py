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
    today_date = datetime.now().strftime("%Y-%m-%d")
    today_active = db.execute("SELECT COUNT(*) as c FROM users WHERE last_launch LIKE ?", (today_date + "%",)).fetchone()["c"]
    users = db.execute("SELECT * FROM users ORDER BY last_launch DESC").fetchall()

    rows = ""
    for u in users:
        d = dict(u)
        rows += f"<tr><td>{d['device_id'][:8]}...</td><td>{d['version']}</td><td>{d['model']}</td><td>{d['first_launch'][:16]}</td><td>{d['last_launch'][:16]}</td><td>{d['launch_count']}</td></tr>"

    return f"""<!DOCTYPE html>
<html><head><meta charset=utf-8><title>AccountBook Analytics</title>
<style>
body { font-family: -apple-system, sans-serif; margin: 20px; background: #f5f5f5; }
.card { background: #fff; border-radius: 8px; padding: 20px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stats { display: flex; gap: 20px; }
.stat-box { background: #2196F3; color: #fff; padding: 15px 25px; border-radius: 8px; text-align: center; }
.stat-box h2 { margin: 0; font-size: 28px; } .stat-box p { margin: 5px 0 0; font-size: 14px; opacity: 0.9; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
th { background: #f8f8f8; font-weight: 600; color: #555; }
tr:hover { background: #f0f7ff; }
</style></head><body>
<div class=card><h1>AccountBook Analytics</h1>
<div class=stats>
<div class=stat-box><h2>{total}</h2><p>Total Users</p></div>
<div class=stat-box><h2>{today_active}</h2><p>Today Active</p></div>
</div></div>
<div class=card><h3>User Details</h3>
<table><thead><tr><th>Device</th><th>Version</th><th>Model</th><th>First Launch</th><th>Last Launch</th><th>Count</th></tr></thead>
<tbody>{rows}</tbody></table></div></body></html>"""

@app.route("/api/stats")
def api_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    today_date = datetime.now().strftime("%Y-%m-%d")
    today_active = db.execute("SELECT COUNT(*) as c FROM users WHERE last_launch LIKE ?", (today_date + "%",)).fetchone()["c"]
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
