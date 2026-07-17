from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="movie_app"
    )


@app.route("/")
def home():
    return "Movie website backend is running!"


@app.route("/movies")
def get_movies():
    search = request.args.get("search", "")
    genre = request.args.get("genre", "")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE %s"
        params.append(f"%{search}%")

    if genre:
        query += " AND genre LIKE %s"
        params.append(f"%{genre}%")

    query += " LIMIT 50"

    cursor.execute(query, params)
    movies = cursor.fetchall()
    conn.close()
    return jsonify(movies)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": str(err)}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user_id": user["user_id"],
        "username": user["username"],
        "is_admin": bool(user["is_admin"])
    }), 200


@app.route("/rate", methods=["POST"])
def rate_movie():
    data = request.get_json()
    user_id = data.get("user_id")
    movie_id = data.get("movie_id")
    rating = data.get("rating")

    if not user_id or not movie_id or rating is None:
        return jsonify({"error": "user_id, movie_id, and rating are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO ratings (user_id, movie_id, rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = %s
        """, (user_id, movie_id, rating, rating))
        conn.commit()

        cursor.execute("SELECT AVG(rating) as avg_rating FROM ratings WHERE movie_id = %s", (movie_id,))
        avg_result = cursor.fetchone()
        new_avg = avg_result[0]

        cursor.execute("UPDATE movies SET user_rating_avg = %s WHERE movie_id = %s", (new_avg, movie_id))
        conn.commit()

        conn.close()
        return jsonify({"message": "Rating submitted successfully", "new_avg_rating": float(new_avg)}), 200

    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": str(err)}), 400


@app.route("/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.get_json()
    user_id = data.get("user_id")
    movie_id = data.get("movie_id")

    if not user_id or not movie_id:
        return jsonify({"error": "user_id and movie_id are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO watchlist (user_id, movie_id) VALUES (%s, %s)",
            (user_id, movie_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Added to watchlist"}), 201
    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": "Already in watchlist or invalid data"}), 400


@app.route("/watchlist/<int:user_id>", methods=["GET"])
def get_watchlist(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT movies.* FROM movies
        JOIN watchlist ON movies.movie_id = watchlist.movie_id
        WHERE watchlist.user_id = %s
    """, (user_id,))
    movies = cursor.fetchall()
    conn.close()
    return jsonify(movies)


@app.route("/recommendations/<int:user_id>")
def get_recommendations(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT movies.genre FROM ratings
        JOIN movies ON ratings.movie_id = movies.movie_id
        WHERE ratings.user_id = %s AND ratings.rating >= 4
    """, (user_id,))
    liked_genres_rows = cursor.fetchall()

    cursor.execute("SELECT movie_id FROM ratings WHERE user_id = %s", (user_id,))
    already_rated = [row["movie_id"] for row in cursor.fetchall()]
    already_rated_ids = tuple(already_rated) if already_rated else (0,)

    if not liked_genres_rows:
        query = f"""
            SELECT * FROM movies
            WHERE movie_id NOT IN {already_rated_ids}
            ORDER BY avg_rating DESC
            LIMIT 12
        """
        cursor.execute(query)
        movies = cursor.fetchall()
        conn.close()
        return jsonify({"based_on": "top_rated", "movies": movies})

    genre_counter = {}
    for row in liked_genres_rows:
        if row["genre"]:
            for g in row["genre"].split(", "):
                genre_counter[g] = genre_counter.get(g, 0) + 1

    top_genres = sorted(genre_counter, key=genre_counter.get, reverse=True)[:3]

    genre_conditions = " OR ".join(["genre LIKE %s"] * len(top_genres))
    params = [f"%{g}%" for g in top_genres]

    query = f"""
        SELECT * FROM movies
        WHERE ({genre_conditions})
        AND movie_id NOT IN {already_rated_ids}
        ORDER BY avg_rating DESC
        LIMIT 12
    """
    cursor.execute(query, params)
    movies = cursor.fetchall()
    conn.close()

    return jsonify({"based_on": "your_taste", "top_genres": top_genres, "movies": movies})

@app.route("/admin/movies", methods=["POST"])
def add_movie():
    data = request.get_json()
    title = data.get("title")
    genre = data.get("genre")
    release_year = data.get("release_year")
    description = data.get("description")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movies (title, genre, release_year, description)
        VALUES (%s, %s, %s, %s)
    """, (title, genre, release_year, description))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Movie added successfully", "movie_id": new_id}), 201


@app.route("/admin/movies/<int:movie_id>", methods=["PUT"])
def edit_movie(movie_id):
    data = request.get_json()
    title = data.get("title")
    genre = data.get("genre")
    release_year = data.get("release_year")
    description = data.get("description")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE movies
        SET title = %s, genre = %s, release_year = %s, description = %s
        WHERE movie_id = %s
    """, (title, genre, release_year, description, movie_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Movie updated successfully"}), 200


@app.route("/admin/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Movie deleted successfully"}), 200
if __name__ == "__main__":
    app.run(debug=True, threaded=True)