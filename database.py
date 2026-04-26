import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS user_info (
    key TEXT PRIMARY KEY,
    value TEXT
)
''')
conn.commit()


def set_info(key, value):
    key = key.strip().lower()
    value = value.strip()

    c.execute(
        "INSERT OR REPLACE INTO user_info (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()


def get_info(key):
    key = key.strip().lower()

    c.execute("SELECT value FROM user_info WHERE key=?", (key,))
    row = c.fetchone()

    return row[0] if row else None


def get_all_info():
    c.execute("SELECT key, value FROM user_info")
    return c.fetchall()