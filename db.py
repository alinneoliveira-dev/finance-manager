from mysql.connector import pooling
from config import Config

dbconfig = {
    "host": Config.MYSQL_HOST,
    "user": Config.MYSQL_USER,
    "password": Config.MYSQL_PASSWORD,
    "database": Config.MYSQL_DATABASE,
    "port": Config.MYSQL_PORT,
}

pool = pooling.MySQLConnectionPool(pool_name="expense_pool", pool_size=5, **dbconfig)


def get_connection():
    return pool.get_connection()
