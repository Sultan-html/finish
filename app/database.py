import sqlite3


connect = sqlite3.connect('basetobot.db')
cursor = connect.cursor

cursor = connect.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            user_id INTEGER,
            task TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
connect.commit()
