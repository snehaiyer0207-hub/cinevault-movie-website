import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor()

cursor.execute("ALTER TABLE movies ADD COLUMN poster_url VARCHAR(500) DEFAULT NULL")
conn.commit()

print("poster_url column added")
conn.close()
