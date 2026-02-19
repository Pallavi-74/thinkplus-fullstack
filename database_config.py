import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host':'localhost',
    'user':'root',
    'password':'',
    'database':'thinkplus'
}
def get_connection():
    try:
        connection = mysql.connector.connect(
            host = DB_CONFIG['host'],
            user = DB_CONFIG['user'],
            password = DB_CONFIG['password'],
            database = DB_CONFIG['database']
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to Mysql:{e}")
        return None