document.getElementById("register-form").addEventListener("submit", function(e) {
    e.preventDefault(); // stops the page from refreshing

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById("message");
        if (data.error) {
            msg.textContent = "Error: " + data.error;
            msg.style.color = "red";
        } else {
            msg.textContent = data.message + " You can now log in.";
            msg.style.color = "green";
        }
    })
    .catch(err => console.error(err));
});