import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE movies 
    ADD COLUMN user_rating_avg DECIMAL(3,2) DEFAULT NULL
""")

conn.commit()
print("Column added successfully")
conn.close()