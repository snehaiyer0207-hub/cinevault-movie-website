import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

for user in users:
    print(user)

conn.close()