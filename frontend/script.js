
const form = document.getElementById("application-form");
const message = document.getElementById("message");

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const data = {
        first_name: document.getElementById("first_name").value,
        last_name: document.getElementById("last_name").value,
        date_of_birth: document.getElementById("date_of_birth").value,
        gender: document.getElementById("gender").value,
        citizenship: document.getElementById("citizenship").value,
        residential_address: document.getElementById("residential_address").value,
        phone_number: document.getElementById("phone_number").value,
        email: document.getElementById("email").value
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/applications", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Ariza yuborilmadi");
        }

        message.textContent = "Ariza muvaffaqiyatli yuborildi!";
        message.style.color = "green";

        form.reset();

    } catch (error) {
        message.textContent = "Xatolik: " + error.message;
        message.style.color = "red";
    }
});
