
const form = document.getElementById("login-form");
const message = document.getElementById("login-message");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/hr/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Tizimga kirib bo'lmadi");
        }

        sessionStorage.setItem("hr_token", result.access_token);

       message.textContent = "Kirish muvaffaqiyatli!";

       window.location.href = "hr-dashboard.html";
        message.style.color = "green";



    } catch (error) {
        message.textContent = "Xatolik: " + error.message;
        message.style.color = "red";
    }
});
