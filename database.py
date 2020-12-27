import sqlite3

DB_NAME = "email-sever.db"


class DBClient:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

    def transaction_operation(self, command, values):
        self.cursor.execute(command, values)
        self.conn.commit()
        self.conn.close()

    def search_one(self, table_name, value, attributes="*", condition="id"):
        self.cursor.execute(
            f"SELECT {attributes} FROM {table_name} WHERE {condition} = ?", (value,)
        )
        return self.cursor.fetchone()

    def search_all(self, table_name, value, attributes="*", condition="id"):
        self.cursor.execute(
            f"SELECT {attributes} FROM {table_name} WHERE {condition} = ?", (value,)
        )
        return self.cursor.fetchall()

    def create_table(self):
        table_user = """
        CREATE TABLE IF NOT EXISTS "user" (
            "id" INTEGER PRIMARY KEY,
            "name" TEXT NOT NULL UNIQUE
        );
        """
        table_message = """
        CREATE TABLE IF NOT EXISTS "message" (
            "id" INTEGER PRIMARY KEY,
            "sender" INTEGER,
            "receiver" INTEGER,
            "subject" TEXT NOT NULL,
            "body" TEXT NOT NULL,
            "reply" INTEGER,
            FOREIGN KEY(sender) REFERENCES user(id),
            FOREIGN KEY(receiver) REFERENCES user(id),
            FOREIGN KEY(reply) REFERENCES message(id)
        );
        """
        self.cursor.execute(table_user)
        self.cursor.execute(table_message)
