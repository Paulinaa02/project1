import sqlite3
from datetime import date


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('todo.db')
        self.cursor = self.conn.cursor()
        self.create_task_table()

    def create_task_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT
            )
        ''')
        self.conn.commit()

    def add_todo(self, title, description, date_text, time_text):
        self.cursor.execute('''
            INSERT INTO todo (title, description, date, time) VALUES (?, ?, ?, ?)
        ''', (title, description, date_text, time_text))
        self.conn.commit()

    def get_todos_for_date(self, date_text):
        self.cursor.execute('''
            SELECT * FROM todo WHERE date = ?
        ''', (date_text,))
        return self.cursor.fetchall()

    def delete_todo_by_id(self, todo_id):
        self.cursor.execute('''
            DELETE FROM todo WHERE id = ?
        ''', (todo_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
