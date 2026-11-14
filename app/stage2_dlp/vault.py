import sqlite3
from datetime import datetime, timedelta
from app.config import DB_PATH, FERNET
from app.telemetry.logger import init_db

def store_in_vault(tokens_map: dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    expires = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    for token, data in tokens_map.items():
        encrypted_val = FERNET.encrypt(data['value'].encode()).decode()
        c.execute("INSERT OR REPLACE INTO vault (token_id, encrypted_value, entity_type, expires_at) VALUES (?, ?, ?, ?)",
                  (token, encrypted_val, data['type'], expires))
    conn.commit()
    conn.close()

def retrieve_from_vault(token_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT encrypted_value, expires_at FROM vault WHERE token_id = ?", (token_id,))
    row = c.fetchone()
    conn.close()
    
    if not row: return None
    encrypted_val, expires_at = row
    if datetime.fromisoformat(expires_at) < datetime.now():
        return None
        
    return FERNET.decrypt(encrypted_val.encode()).decode()