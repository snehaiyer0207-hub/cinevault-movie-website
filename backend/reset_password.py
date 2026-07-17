import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor()

email = "snehaiyer0207@gmail.com"  # change to your account's email
new_password = "Sneha@123"      # change to whatever new password you want

hashed = generate_password_hash(new_password)
cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))
conn.commit()

print(f"Rows updated: {cursor.rowcount}")
conn.close()