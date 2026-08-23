from contextlib import contextmanager
from mysql.connector import pooling
from config import Config

dbconfig = {
    "host": Config.MYSQL_HOST,
    "user": Config.MYSQL_USER,
    "password": Config.MYSQL_PASSWORD,
    "database": Config.MYSQL_DATABASE,
    "port": Config.MYSQL_PORT,
}

pool = pooling.MySQLConnectionPool(pool_name="expense_pool", pool_size=10, **dbconfig)


def get_connection():
    return pool.get_connection()


@contextmanager
def get_cursor(dictionary=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
