import sqlite3
from app.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    stage TEXT,
                    verdict TEXT,
                    threat_category TEXT,
                    latency_ms REAL,
                    user_role TEXT,
                    tokens_masked INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vault (
                    token_id TEXT PRIMARY KEY,
                    encrypted_value TEXT,
                    entity_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME
                )''')
    conn.commit()
    conn.close()

def log_event(stage, verdict, threat_category, latency_ms, user_role="Guest", tokens_masked=0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO telemetry (stage, verdict, threat_category, latency_ms, user_role, tokens_masked) VALUES (?, ?, ?, ?, ?, ?)",
              (stage, verdict, threat_category, latency_ms, user_role, tokens_masked))
    conn.commit()
    conn.close()