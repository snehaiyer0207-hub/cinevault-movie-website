import pandas as pd
import mysql.connector
import ast  # to safely parse the genre data

# Load the CSV
df = pd.read_csv("tmdb_5000_movies.csv")

# Connect to MySQL
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
    
    # genres column looks like: [{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}]
    try:
        genres_list = ast.literal_eval(row['genres'])
        genre = ", ".join([g['name'] for g in genres_list])
    except:
        genre = None
    
    # release_date looks like "2009-12-10" -> we just want the year
    try:
        release_year = int(str(row['release_date'])[:4])
    except:
        release_year = None
    
    description = row['overview'] if pd.notna(row['overview']) else None
    
    sql = """
    INSERT INTO movies (title, genre, release_year, description, avg_rating)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (title, genre, release_year, description, row['vote_average'])
    
    cursor.execute(sql, values)
    count += 1

conn.commit()
print(f"Inserted {count} movies successfully!")

conn.close()