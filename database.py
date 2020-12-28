import os

import psycopg2

DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


def connect_to_database():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    return conn, cursor


def transaction_operation(command: str, values: tuple, return_id: bool = False):
    conn, cursor = connect_to_database()
    cursor.execute(command, values)
    id = None
    if return_id:
        id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return id


def search_in_database(command: str, values: tuple, one: bool = True):
    conn, cursor = connect_to_database()
    cursor.execute(command, values)
    result = cursor.fetchone() if one else cursor.fetchall()
    conn.close()
    return result


def find_user(name: str = None, id: int = -1):
    sql = "SELECT * FROM public.user WHERE"
    if name is not None:
        sql += " name LIKE (%s)"
        return search_in_database(command=sql, values=(name,))
    sql += " id = (%s)"
    return search_in_database(command=sql, values=(id,))


def find_message(id: int = -1, receiver: int = -1, sender: int = -1):
    sql = "SELECT DISTINCT * FROM public.message WHERE id = (%s) OR receiver = (%s) OR sender = (%s)"
    return search_in_database(
        command=sql, values=(id, receiver, sender), one=(id != -1)
    )
