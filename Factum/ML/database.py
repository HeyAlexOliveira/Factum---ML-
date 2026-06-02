
import sqlite3

DB_NAME = "factum.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            result TEXT,
            source TEXT
        )
    ''')

    conn.commit()
    conn.close()

def save_prediction(text, result, source):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO predictions (text, result, source) VALUES (?, ?, ?)",
        (text, result, source)
    )

    conn.commit()
    conn.close()
