import pandas as pd
import mysql.connector

# Load the CSV
df = pd.read_csv("bollywood_movies.csv")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor()

count = 0

for index, row in df.iterrows():
    title = row['title']

    try:
        release_year = int(row['year'])
    except:
        release_year = None

    try:
        rating = float(row['rating'])
    except:
        rating = None

    genre = "Bollywood"  # tagging all of these as Bollywood since no genre column exists
    description = None

    sql = """
    INSERT INTO movies (title, genre, release_year, description, avg_rating)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (title, genre, release_year, description, rating)

    cursor.execute(sql, values)
    count += 1

conn.commit()
print(f"Inserted {count} Bollywood movies successfully!")

conn.close()