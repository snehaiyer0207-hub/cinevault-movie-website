const storedUser = localStorage.getItem("user");
const authDiv = document.getElementById("auth-status");

if (storedUser) {
    const user = JSON.parse(storedUser);
    authDiv.innerHTML = `Signed in as <strong>${user.username}</strong> · <a href="watchlist.html">My Watchlist</a> · <a href="#" id="logout-link">Logout</a>`;
    document.getElementById("logout-link").addEventListener("click", function() {
        localStorage.removeItem("user");
        location.reload();
    });
} else {
    authDiv.innerHTML = `<a href="login.html">Login</a> · <a href="register.html">Register</a>`;
}

if (!storedUser) {
    document.getElementById("rec-subtitle").textContent = "Please log in to see personalized recommendations.";
} else {
    const user = JSON.parse(storedUser);

    fetch(`http://127.0.0.1:5000/recommendations/${user.user_id}`)
        .then(response => response.json())
        .then(data => {
            const subtitle = document.getElementById("rec-subtitle");
            const container = document.getElementById("movie-list");

            if (data.based_on === "top_rated") {
                subtitle.textContent = "Rate a few movies to get personalized picks. For now, here are top-rated movies.";
            } else {
                subtitle.textContent = "Based on your taste for: " + data.top_genres.join(", ");
            }

            if (data.movies.length === 0) {
                container.innerHTML = "<p>No recommendations available yet — try rating a few more movies.</p>";
                return;
            }

            data.movies.forEach(movie => {
                const div = document.createElement("div");
                div.classList.add("movie-card");

                const posterClass = "poster-" + (movie.movie_id % 5);
                const initial = movie.title ? movie.title.charAt(0).toUpperCase() : "?";

                const ratingButtons = `
                    <div class="action-row">
                        <button onclick="rateMovie(${movie.movie_id}, 1)">1</button>
                        <button onclick="rateMovie(${movie.movie_id}, 2)">2</button>
                        <button onclick="rateMovie(${movie.movie_id}, 3)">3</button>
                        <button onclick="rateMovie(${movie.movie_id}, 4)">4</button>
                        <button onclick="rateMovie(${movie.movie_id}, 5)">5</button>
                        <button class="watchlist-btn" onclick="addToWatchlist(${movie.movie_id})">+ Watchlist</button>
                    </div>
                `;

                const tmdbScore = movie.avg_rating ? `TMDB: ${parseFloat(movie.avg_rating).toFixed(1)}/10` : "TMDB: N/A";
                const userScore = movie.user_rating_avg ? `Users: ${parseFloat(movie.user_rating_avg).toFixed(1)}/5` : "Users: Not rated yet";

                div.innerHTML = `
                    <div class="poster ${posterClass}">${initial}</div>
                    <div class="movie-info">
                        <h3>${movie.title}</h3>
                        <p>${movie.genre || "Unknown genre"} ${movie.release_year ? "· " + movie.release_year : ""}</p>
                        <p class="rating-line">${tmdbScore}</p>
                        <p class="rating-line">${userScore}</p>
                        ${ratingButtons}
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(error => console.error("Error fetching recommendations:", error));
}

function rateMovie(movieId, rating) {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
        alert("Please log in to rate movies.");
        return;
    }

    fetch("http://127.0.0.1:5000/rate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: user.user_id,
            movie_id: movieId,
            rating: rating
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("Rated successfully!");
            location.reload();
        }
    })
    .catch(err => console.error(err));
}

function addToWatchlist(movieId) {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
        alert("Please log in to add movies to your watchlist.");
        return;
    }

    fetch("http://127.0.0.1:5000/watchlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: user.user_id,
            movie_id: movieId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert("Added to watchlist!");
        }
    })
    .catch(err => console.error(err));
}