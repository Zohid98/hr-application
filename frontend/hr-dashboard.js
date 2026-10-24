
const token = sessionStorage.getItem("hr_token");

const message = document.getElementById("message");
const applicationsBody = document.getElementById("applications-body");
const logoutButton = document.getElementById("logout-button");

if (!token) {
    window.location.href = "hr-login.html";
}

async function loadApplications() {
    try {
        const response = await fetch(
            "http://127.0.0.1:8000/applications",
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.status === 401 || response.status === 403) {
            sessionStorage.removeItem("hr_token");
            window.location.href = "hr-login.html";
            return;
        }

        if (!response.ok) {
            throw new Error("Arizalarni olishda xatolik yuz berdi");
        }

        const applications = await response.json();

        applicationsBody.replaceChildren();

        applications.forEach(function (application) {
            const row = document.createElement("tr");

            const values = [
                application.id,
                application.first_name,
                application.last_name,
                application.phone_number,
                application.email,
                application.status
            ];

            values.forEach(function (value) {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            });

            applicationsBody.appendChild(row);
        });

        message.textContent = `Jami arizalar: ${applications.length}`;
        message.style.color = "green";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
}

logoutButton.addEventListener("click", function () {
    sessionStorage.removeItem("hr_token");
    window.location.href = "hr-login.html";
});

if (token) {
    loadApplications();
}
