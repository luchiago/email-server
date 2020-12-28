import sqlite3

DB_NAME = "email-sever.db"

def connect_to_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

def transaction_operation(command: str, values: tuple):
    conn, cursor = connect_to_database()
    cursor.execute(command, values)
    conn.commit()
    conn.close()

def search_in_database(command: str, values: tuple, one: bool = True):
    conn, cursor = connect_to_database()
    cursor.execute(command, values)
    result = cursor.fetchone() if one else cursor.fetchall()
    conn.close()
    return result

def find_user(name: str = None, id: int = -1):
    sql = "SELECT * FROM user WHERE"
    if name is not None:
        sql += " name LIKE ?"
        return search_in_database(command=sql, values=(name,))
    sql += " id = ?"
    return search_in_database(command=sql, values=(id,))

def find_message(id: int = -1, receiver: int = -1, sender: int = -1):
    sql = (
        "SELECT DISTINCT * FROM message WHERE id = ? OR receiver = ? OR sender = ?"
    )
    return search_in_database(
        command=sql, values=(id, receiver, sender), one=(id != -1)
    )

def create_table():
    conn, cursor = connect_to_database()
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
    cursor.execute(table_user)
    cursor.execute(table_message)
    conn.close()
