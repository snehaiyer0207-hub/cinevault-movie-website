import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""   # leave blank unless you set one in XAMPP
)

if conn.is_connected():
    print("Connected to MySQL successfully!")

conn.close()