const storedUser = localStorage.getItem("user");
const authDiv = document.getElementById("auth-status");
const user = storedUser ? JSON.parse(storedUser) : null;

if (!user) {
    document.body.innerHTML = "<p style='padding:32px;'>Please log in.</p>";
} else if (!user.is_admin) {
    document.body.innerHTML = "<p style='padding:32px;'>Access denied. Admins only.</p>";
} else {
    authDiv.innerHTML = `Signed in as <strong>${user.username}</strong> (Admin) · <a href="#" id="logout-link">Logout</a>`;
    document.getElementById("logout-link").addEventListener("click", function() {
        localStorage.removeItem("user");
        location.reload();
    });
    loadAdminMovies();
}

function submitMovie() {
    const movieId = document.getElementById("edit-movie-id").value;
    const title = document.getElementById("movie-title").value;
    const genre = document.getElementById("movie-genre").value;
    const release_year = document.getElementById("movie-year").value;
    const description = document.getElementById("movie-description").value;

    if (!title) {
        alert("Title is required.");
        return;
    }

    const payload = { title, genre, release_year: release_year ? parseInt(release_year) : null, description };

    const url = movieId
        ? `http://127.0.0.1:5000/admin/movies/${movieId}`
        : `http://127.0.0.1:5000/admin/movies`;
    const method = movieId ? "PUT" : "POST";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("admin-message").textContent = data.message || data.error;
        resetForm();
        loadAdminMovies();
    })
    .catch(err => console.error(err));
}

function resetForm() {
    document.getElementById("edit-movie-id").value = "";
    document.getElementById("movie-title").value = "";
    document.getElementById("movie-genre").value = "";
    document.getElementById("movie-year").value = "";
    document.getElementById("movie-description").value = "";
    document.getElementById("form-title").textContent = "Add New Movie";
}

function editMovie(movie) {
    document.getElementById("edit-movie-id").value = movie.movie_id;
    document.getElementById("movie-title").value = movie.title;
    document.getElementById("movie-genre").value = movie.genre || "";
    document.getElementById("movie-year").value = movie.release_year || "";
    document.getElementById("movie-description").value = movie.description || "";
    document.getElementById("form-title").textContent = "Edit Movie: " + movie.title;
    window.scrollTo(0, 0);
}

function deleteMovie(movieId, title) {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;

    fetch(`http://127.0.0.1:5000/admin/movies/${movieId}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            document.getElementById("admin-message").textContent = data.message;
            loadAdminMovies();
        })
        .catch(err => console.error(err));
}

function loadAdminMovies() {
    fetch("http://127.0.0.1:5000/movies")
        .then(res => res.json())
        .then(movies => {
            const container = document.getElementById("movie-list");
            container.innerHTML = "";

            movies.forEach(movie => {
                const div = document.createElement("div");
                div.classList.add("movie-card");

                const posterClass = "poster-" + (movie.movie_id % 5);
                const initial = movie.title ? movie.title.charAt(0).toUpperCase() : "?";

                div.innerHTML = `
                    <div class="poster ${posterClass}">${initial}</div>
                    <div class="movie-info">
                        <h3>${movie.title}</h3>
                        <p>${movie.genre || "Unknown genre"} ${movie.release_year ? "· " + movie.release_year : ""}</p>
                        <div class="action-row">
                            <button class="watchlist-btn" style="border-radius:6px;width:auto;padding:0 12px;" onclick='editMovie(${JSON.stringify(movie)})'>Edit</button>
                            <button class="watchlist-btn" style="border-radius:6px;width:auto;padding:0 12px;background:#6a1b1b !important;" onclick="deleteMovie(${movie.movie_id}, '${movie.title.replace(/'/g, "\\'")}')">Delete</button>
                        </div>
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(err => console.error(err));
}