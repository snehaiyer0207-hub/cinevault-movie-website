import mysql.connector
import requests
import time

API_KEY = "658b12ec"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_app"
)
cursor = conn.cursor(dictionary=True)

# Get movies that don't have a poster yet, prioritize highest rated first
cursor.execute("""
    SELECT movie_id, title, release_year FROM movies
    WHERE poster_url IS NULL
    ORDER BY avg_rating DESC
    LIMIT 5
""")
movies = cursor.fetchall()

update_cursor = conn.cursor()
count = 0

for movie in movies:
    title = movie["title"]
    year = movie["release_year"]

    try:
        url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
        if year:
            url += f"&y={year}"

        response = requests.get(url, timeout=5)
        data = response.json()
        print(title, "->", data)

        poster = data.get("Poster")

        if poster and poster != "N/A":
            update_cursor.execute(
                "UPDATE movies SET poster_url = %s WHERE movie_id = %s",
                (poster, movie["movie_id"])
            )
            count += 1
        else:
            update_cursor.execute(
                "UPDATE movies SET poster_url = %s WHERE movie_id = %s",
                ("none", movie["movie_id"])
            )

    except Exception as e:
        print(f"Error on {title}: {e}")

    time.sleep(0.05)

conn.commit()
print(f"Fetched {count} posters successfully!")
conn.close()