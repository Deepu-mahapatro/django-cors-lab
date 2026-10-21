
const API_URL = "http://127.0.0.1:8000/api/";

const output = document.getElementById("output");
const origin = document.getElementById("origin");
const getButton = document.getElementById("getButton");
const postButton = document.getElementById("postButton");

origin.textContent = window.location.origin;

// GET request
getButton.addEventListener("click", async () => {
    output.textContent = "Sending GET request...";

    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        output.textContent = JSON.stringify({
            httpStatus: response.status,
            data,
        }, null, 2);
    } catch (error) {
        output.textContent = "GET failed: " + error.message;
    }
});

// JSON POST request with CSRF protection
postButton.addEventListener("click", async () => {
    output.textContent = "Obtaining CSRF token...";

    try {
        // Step 1: Obtain the CSRF token and cookie.
        const csrfResponse = await fetch(API_URL + "csrf/", {
            credentials: "include",
        });

        if (!csrfResponse.ok) {
            throw new Error(
                "CSRF endpoint returned " + csrfResponse.status
            );
        }

        const csrfData = await csrfResponse.json();

        // Step 2: Send POST with the cookie and CSRF token.
        const response = await fetch(API_URL, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfData.csrfToken,
            },
            body: JSON.stringify({
                name: "Laptop",
            }),
        });

        const responseText = await response.text();

        output.textContent = JSON.stringify({
            httpStatus: response.status,
            responseBody: responseText,
        }, null, 2);

    } catch (error) {
        output.textContent = "POST failed: " + error.message;
    }
});
