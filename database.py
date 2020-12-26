import sqlite3

DB_NAME = "email-sever.db"


class DBClient:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
