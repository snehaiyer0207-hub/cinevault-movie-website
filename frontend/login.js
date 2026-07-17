document.getElementById("login-form").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById("message");
        if (data.error) {
            msg.textContent = "Error: " + data.error;
            msg.style.color = "red";
        } else {
            localStorage.setItem("user", JSON.stringify(data));
            msg.textContent = "Login successful! Redirecting...";
            msg.style.color = "green";
            setTimeout(() => {
                window.location.href = "index.html";
            }, 1000);
        }
    })
    .catch(err => console.error(err));
});