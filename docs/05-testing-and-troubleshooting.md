# Testing and Troubleshooting — Django CORS Learning Lab

## 1. What Are We Testing?

The purpose of testing this project is to verify that the frontend can communicate with the Django backend while the configured CORS policy and Django's CSRF protection remain enabled.

Our tests cover four important areas:

- **Connectivity:** Can the frontend reach the Django server?
- **CORS:** Does the backend permit the configured frontend origin?
- **Preflight:** Does the middleware approve or reject qualifying OPTIONS requests correctly?
- **CSRF:** Does Django reject unsafe requests without valid CSRF information and accept a correctly configured request?

### Project URLs

| Component | URL |
|---|---|
| Frontend | `http://127.0.0.1:5500` |
| Backend API | `http://127.0.0.1:8000/api/` |
| CSRF endpoint | `http://127.0.0.1:8000/api/csrf/` |

The frontend should use `127.0.0.1` consistently for the backend rather than switching between `localhost` and `127.0.0.1`.

---

## 2. Prepare the Development Environment

Before testing, verify that the project structure is correct:

```text
django-cors-lab/
├── backend/
│   ├── venv/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   └── api/
│       ├── views.py
│       ├── urls.py
│       └── middleware.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── docs/
│   ├── 01-project-architecture.md
│   ├── 02-cors-fundamentals.md
│   ├── 03-options-preflight-flow.md
│   ├── 04-csrf-protection-flow.md
│   └── 05-testing-and-troubleshooting.md
├── .gitignore
└── README.md
```

### Start the Django backend

Open a terminal in the project root:

```bash
cd backend
```

Activate the virtual environment on Windows Command Prompt:

```bat
venv\Scripts\activate
```

Run Django's system checks:

```bash
python manage.py check
```

Start the development server:

```bash
python manage.py runserver 127.0.0.1:8000
```

### Start the frontend

Open the `frontend/index.html` file using VS Code Live Server and configure it to use port `5500`.

Verify that the browser origin is:

```text
http://127.0.0.1:5500
```

If Live Server uses a different port, update `ALLOWED_ORIGINS` and the relevant trusted-origin configuration to match the actual origin.

---

## 3. Test Basic Backend Connectivity

First, test the API without involving the frontend.

Open this URL in a browser or send a GET request from Postman:

```text
http://127.0.0.1:8000/api/
```

Expected response:

```json
{
    "message": "Welcome to Django CORS Learning Lab!",
    "status": "success",
    "backend": "Django"
}
```

Expected status:

```text
200 OK
```

### What does this test prove?

It confirms that:

- Django is running.
- The `/api/` URL resolves successfully.
- The `home()` view returns JSON.

However, a successful direct GET does not prove that browser CORS or CSRF behavior is working correctly. Those require separate tests.

---

## 4. Test the CSRF Token Endpoint

Send a GET request to:

```text
http://127.0.0.1:8000/api/csrf/
```

Expected status:

```text
200 OK
```

Example response:

```json
{
    "csrfToken": "your-generated-token"
}
```

The actual token is generated dynamically by Django.

### What should you verify?

1. The response contains a `csrfToken` field.
2. The response sets the CSRF cookie when the request and cookie settings permit it.
3. The browser or Postman retains the cookie for the backend host.
4. The next unsafe request sends the token and matching cookie.

In browser developer tools, inspect the Network tab and the response headers for `Set-Cookie`. Also inspect the browser's cookie storage if the cookie appears to be missing.

A token appearing in JSON alone does not prove that the corresponding cookie was stored or sent.

---

## 5. Test the OPTIONS Preflight

Our custom middleware recognizes a preflight when the request method is OPTIONS and the `Access-Control-Request-Method` header is present.

In Postman, create a request with the following details.

**Method:** `OPTIONS`

**URL:**

```text
http://127.0.0.1:8000/api/
```

**Headers:**

| Key | Value |
|---|---|
| `Origin` | `http://127.0.0.1:5500` |
| `Access-Control-Request-Method` | `POST` |
| `Access-Control-Request-Headers` | `content-type,x-csrftoken` |

Expected result:

```text
204 No Content
```

Check that the response contains appropriate CORS headers, including:

```http
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Methods: DELETE, GET, PATCH, POST
Access-Control-Allow-Headers: Content-Type, Authorization, X-CSRFToken
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 600
```

The exact formatting and ordering of header values may differ, but the requested origin, method, and headers must be permitted.

### Test a rejected origin

Keep the request the same, but change the `Origin` header to:

```text
http://localhost:5500
```

Expected result in our implementation:

```text
403 Forbidden
```

This happens because the configured allowlist contains `http://127.0.0.1:5500`, not `http://localhost:5500`.

**Important:** Postman lets us inspect the middleware response, but it does not enforce browser CORS rules. Test in a browser to verify actual browser behavior.

---

## 6. Test the Actual POST Request

Our frontend POST sends JSON and a CSRF token.

The expected request includes:

```http
POST /api/ HTTP/1.1
Content-Type: application/json
X-CSRFToken: <csrf-token>
```

It also needs the corresponding CSRF cookie to be sent.

### Browser test

1. Open the frontend using Live Server.
2. Open browser developer tools and select the Network tab.
3. Click the GET button and verify that the API returns JSON.
4. Click the POST button.
5. Inspect the Network tab for the CSRF GET, the OPTIONS preflight when applicable, and the actual POST.
6. Check the POST status and response body.

The expected successful result is:

```text
200 OK
```

with the welcome JSON.

### Postman test

1. Send GET to `/api/csrf/`.
2. Confirm the response includes `csrfToken`.
3. Confirm that the matching `csrftoken` cookie is stored for `127.0.0.1`.
4. Send POST to `/api/` with `Content-Type: application/json`.
5. Set `X-CSRFToken` to the token returned by the CSRF endpoint.
6. Ensure the matching cookie is included.
7. Send the request.

The expected result is `200 OK`.

**Current project limitation:** The `/api/` view returns welcome JSON for POST requests. It does not create a Laptop record or persist the submitted JSON in a database. A `200 OK` here confirms the request reached the view, not that a record was saved.

---

## 7. Common Errors and How to Fix Them

| Error | Likely cause | Fix |
|---|---|---|
| `Connection refused` | Django is not running or the URL/port is incorrect | Start the server and check the API URL. |
| `404 Not Found` | Incorrect URL route | Verify `config/urls.py` and `api/urls.py`. |
| `405 Method Not Allowed` | The view or endpoint does not support the method being sent | Check the view's method handling. |
| `403 CSRF cookie not set` | The required CSRF cookie was not sent | Call `/api/csrf/` first and inspect the cookie. |
| CSRF token missing or incorrect | The token header is absent or invalid | Send the token returned by the CSRF endpoint and the matching cookie. |
| OPTIONS returns `403` | Origin, requested method, or requested headers fail the custom allowlist checks | Inspect the three values and compare them with `middleware.py`. |
| Browser reports a CORS error | The browser could not validate the CORS response | Inspect the preflight and actual response headers in DevTools. |
| Cookie is not retained or sent | Host mismatch or cookie policy/configuration issue | Use consistent hosts and inspect cookie attributes and browser rules. |
| Django import warning in VS Code | The editor may be using a different Python interpreter | Select `backend/venv` as the interpreter and reload VS Code. |

### Debugging order

When a request fails, follow this order:

1. Check whether the backend server is running.
2. Verify the request URL, method, and port.
3. Check the browser Network tab or Postman response.
4. If the request uses preflight, inspect the OPTIONS response.
5. If the POST reaches Django but returns 403, inspect the CSRF error details.
6. Check Django's terminal output for additional information.

This order helps distinguish connectivity problems, CORS failures, and CSRF failures instead of treating them as one issue.

---

## 8. Browser CORS Errors vs. Django CSRF Errors

CORS and CSRF solve different security problems.

| CORS | CSRF |
|---|---|
| Controls whether browser JavaScript can access a cross-origin response, subject to the CORS protocol. | Helps prevent forged unsafe requests using browser credentials. |
| Uses headers such as `Access-Control-Allow-Origin`. | Uses CSRF tokens, cookies, and Django's validation rules. |
| May involve an automatic OPTIONS preflight. | Validates unsafe requests such as POST, PATCH, and DELETE. |
| Does not authenticate users. | Does not replace authentication or authorization. |

### Example: CORS failure

The browser sends a preflight, but the server does not return headers that approve the requested origin, method, and headers.

The browser blocks the cross-origin operation. For a failed preflight, it normally does not send the actual request.

### Example: CSRF failure

The preflight succeeds and the browser sends the POST, but Django rejects it because the CSRF cookie or token is missing or invalid.

The request has reached Django's CSRF validation, but it is not allowed to proceed.

### Key diagnostic question

**Did the browser block the request at the CORS stage, or did Django receive and reject the actual request?**

Use the Network tab, response status, response headers, and Django logs to determine which case occurred.

---

## 9. Final Verification Checklist

Before considering the project ready for GitHub, verify the following.

- [ ] Django starts successfully on `127.0.0.1:8000`.
- [ ] `python manage.py check` completes without errors.
- [ ] GET `/api/` returns the expected welcome JSON.
- [ ] GET `/api/csrf/` returns a CSRF token.
- [ ] The CSRF cookie is set and sent where required.
- [ ] The approved-origin OPTIONS test returns `204`.
- [ ] The unapproved-origin OPTIONS test returns `403` in our implementation.
- [ ] Browser GET works from the configured frontend origin.
- [ ] Browser POST succeeds when the CSRF token and cookie are valid.
- [ ] Postman POST succeeds with the matching token and cookie.
- [ ] CSRF protection remains enabled.
- [ ] The root `.gitignore` excludes the virtual environment and sensitive environment files.
- [ ] Real Django secret keys and credentials are not committed.
- [ ] All five documentation files are present in `docs/`.
- [ ] `README.md` explains project setup, testing, and the documentation links.

These checks cover the behavior we implemented and tested. They are not a complete production security audit.

---

## 10. Before Pushing to GitHub

### Review the repository

From the project root, run:

```bash
git status
```

Inspect the staged and unstaged changes carefully. Ensure that `backend/venv/`, local `.env` files, cache files, and other generated artifacts are not being committed.

### Check for secrets

The Django secret key should be loaded from an environment variable for deployment. If a real secret key was exposed in source code or committed previously, replace it and review the repository history as appropriate.

A `.gitignore` prevents future untracked files from being added automatically, but it does not remove files already tracked by Git.

### Stage and commit the project

After reviewing the changes:

```bash
git add .
git status
git commit -m "Document Django CORS and CSRF learning lab"
git push
```

If this is the first push, configure the GitHub remote and branch according to your repository setup.

### Final project outcome

This project demonstrates:

- How a frontend and Django backend communicate across origins.
- How CORS response headers control browser access to cross-origin responses.
- How an OPTIONS preflight is validated by custom middleware.
- How Django's CSRF token and cookie work together for unsafe requests.
- How to test request behavior using Postman and browser developer tools.
- How to diagnose common connectivity, CORS, and CSRF errors.

### Related documentation

- [Project Architecture](01-project-architecture.md)
- [CORS Fundamentals](02-cors-fundamentals.md)
- [OPTIONS Preflight Flow](03-options-preflight-flow.md)
- [CSRF Protection Flow](04-csrf-protection-flow.md)
