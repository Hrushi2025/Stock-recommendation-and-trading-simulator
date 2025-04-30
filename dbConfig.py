# This program is to connect to the database by providing host, user_name,  password , and database name

import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='258925',
    database='stock_project'
)

if conn.is_connected():
    print("Connection SucessFull")
