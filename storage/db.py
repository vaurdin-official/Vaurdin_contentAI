import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        type TEXT,
        content TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_post(topic, post_type, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (topic, type, content) VALUES (?, ?, ?)", (topic, post_type, content))
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, type, content FROM posts ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "topic": r[1], "type": r[2], "content": r[3]} for r in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
