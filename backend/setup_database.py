import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = conn.cursor()

# Create the database
cursor.execute("CREATE DATABASE IF NOT EXISTS movie_app")
print("Database created (or already exists)")

conn.close()