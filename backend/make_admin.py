import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor()

# Change the email below to your actual account's email
cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = %s", ("snehaiyer0207@gmail.com",))
conn.commit()

print(f"Rows updated: {cursor.rowcount}")
conn.close()