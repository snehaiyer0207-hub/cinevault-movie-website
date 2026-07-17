const storedUser = localStorage.getItem("user");
const authDiv = document.getElementById("auth-status");

if (storedUser) {
    const user = JSON.parse(storedUser);
    const adminLink = user.is_admin ? ` · <a href="admin.html">Admin Panel</a>` : "";
    authDiv.innerHTML = `Signed in as <strong>${user.username}</strong> · <a href="recommendations.html">Recommended</a> · <a href="watchlist.html">My Watchlist</a>${adminLink} · <a href="#" id="logout-link">Logout</a>`;
    document.getElementById("logout-link").addEventListener("click", function() {
        localStorage.removeItem("user");
        location.reload();
    });
} else {
    authDiv.innerHTML = `<a href="login.html">Login</a> · <a href="register.html">Register</a>`;
}

const user = storedUser ? JSON.parse(storedUser) : null;

if (!user) {
    document.getElementById("watchlist-container").innerHTML = "<p>Please log in to see your watchlist.</p>";
} else {
    fetch(`http://127.0.0.1:5000/watchlist/${user.user_id}`)
        .then(response => response.json())
        .then(movies => {
            const container = document.getElementById("watchlist-container");

            if (movies.length === 0) {
                container.innerHTML = "<p>Your watchlist is empty.</p>";
                return;
            }

            movies.forEach(movie => {
                const div = document.createElement("div");
                div.classList.add("movie-card");

                const posterClass = "poster-" + (movie.movie_id % 5);
                const initial = movie.title ? movie.title.charAt(0).toUpperCase() : "?";

                const tmdbScore = movie.avg_rating ? `TMDB: ${parseFloat(movie.avg_rating).toFixed(1)}/10` : "TMDB: N/A";
                const userScore = movie.user_rating_avg ? `Users: ${parseFloat(movie.user_rating_avg).toFixed(1)}/5` : "Users: Not rated yet";

                div.innerHTML = `
                    <div class="poster ${posterClass}">${initial}</div>
                    <div class="movie-info">
                        <h3>${movie.title}</h3>
                        <p>${movie.genre || "Unknown genre"} ${movie.release_year ? "· " + movie.release_year : ""}</p>
                        <p class="rating-line">${tmdbScore}</p>
                        <p class="rating-line">${userScore}</p>
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(error => console.error("Error fetching watchlist:", error));
}