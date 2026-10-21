# 🌐 Django CORS & CSRF Learning Lab

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-Backend-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/JavaScript-Fetch_API-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/HTTP-CORS%20%26%20CSRF-005571?style=for-the-badge" alt="HTTP CORS and CSRF">
  <img src="https://img.shields.io/badge/Postman-API_Testing-FF6C37?style=for-the-badge&logo=postman&logoColor=white" alt="Postman">
  <img src="https://img.shields.io/badge/Git-GitHub-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git and GitHub">
</p>

<p align="center">
  <b>A hands-on project to understand Cross-Origin Resource Sharing (CORS), OPTIONS preflight requests, and CSRF protection through practical Django and browser-based API testing.</b>
</p>

---

## 📌 About the Project

This project was built to understand how frontend applications communicate with Django backends running on different origins, and how browsers and Django handle cross-origin requests securely.

Instead of learning CORS and CSRF only through theory, this project demonstrates their behavior through real HTTP requests, custom Django middleware, JavaScript Fetch API calls, browser developer tools, and Postman.

The frontend runs on `127.0.0.1:5500`, while the Django backend runs on `127.0.0.1:8000`.

The project focuses on understanding:

- What CORS is and why browsers enforce it
- The Same-Origin Policy
- How origins differ by scheme, hostname, and port
- How custom Django middleware handles CORS
- Why browsers send OPTIONS preflight requests
- How allowed origins, methods, and headers are validated
- How CORS response headers work
- Why CORS and CSRF are separate security mechanisms
- How Django generates and validates CSRF tokens
- Why cookies and CSRF tokens are needed for unsafe requests
- How to test CORS and CSRF behavior using Postman and browser developer tools
- How to troubleshoot common `403 Forbidden` and browser CORS errors

---

## 🎯 Project Objectives

The primary objective is to understand the complete lifecycle of a cross-origin API request, from frontend JavaScript to Django and back to the browser.

### Primary Objectives

- Understand browser same-origin restrictions
- Configure an explicit CORS origin allowlist
- Implement custom CORS middleware in Django
- Handle qualifying OPTIONS preflight requests
- Validate requested HTTP methods and headers
- Return appropriate CORS response headers
- Understand credentialed cross-origin requests
- Implement a CSRF token endpoint
- Send CSRF tokens through the `X-CSRFToken` header
- Understand the role of CSRF cookies
- Test successful and rejected preflight requests
- Diagnose CORS and CSRF failures independently
- Document the architecture, request flows, and testing process

---

## 🏗️ Architecture

```text
                    ┌──────────────────────────┐
                    │        Frontend          │
                    │     HTML / CSS / JS      │
                    │  127.0.0.1:5500          │
                    └────────────┬─────────────┘
                                 │
                                 │ Fetch API
                                 ▼
                    ┌──────────────────────────┐
                    │      Browser CORS        │
                    │   Preflight Evaluation   │
                    └────────────┬─────────────┘
                                 │
                       OPTIONS / Actual Request
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       Django API         │
                    │  127.0.0.1:8000          │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   ManualCORSMiddleware   │
                    │ Origin / Method / Header │
                    │       Validation         │
                    └────────────┬─────────────┘
                                 │
                      Actual request continues
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Django CSRF Middleware │
                    │  Token / Cookie Checks   │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       API Views          │
                    │ Welcome JSON / CSRF Token│
                    └──────────────────────────┘
```

### Core Principle

> **CORS controls browser access to cross-origin responses, while CSRF protection helps prevent forged unsafe requests. They solve different security problems.**

The browser enforces CORS rules. Django's middleware validates the configured CORS policy and applies CSRF protection to the actual request.

---

## 🔄 End-to-End Request Flow

The project demonstrates two main request paths.

### 1. GET Request

```text
Frontend JavaScript
        ↓
GET /api/
        ↓
Django CORS Middleware
        ↓
API View
        ↓
Welcome JSON
        ↓
Browser Displays Response
```

The GET endpoint returns a JSON response from Django. Depending on the request characteristics, a cross-origin GET may not require an OPTIONS preflight.

### 2. POST Request with CSRF Protection

```text
Frontend JavaScript
        ↓
GET /api/csrf/
        ↓
Django Returns CSRF Token
and Sets CSRF Cookie
        ↓
Browser Sends OPTIONS Preflight
        ↓
Django Validates Origin,
Method and Requested Headers
        ↓
204 No Content
        ↓
Browser Sends Actual POST
with CSRF Token and Cookie
        ↓
Django CSRF Middleware
Validates Request
        ↓
API View Returns JSON
```

If preflight fails, the browser normally does not send the actual POST. If CSRF validation fails, Django can reject the POST even after a successful preflight.

---

## ⚡ CORS Features Implemented

| Feature | Implementation |
|---|---|
| Origin Allowlist | Allows the configured frontend origin |
| Method Validation | Checks requested methods against an allowlist |
| Header Validation | Checks requested headers against an allowlist |
| OPTIONS Preflight | Handles qualifying OPTIONS requests |
| Successful Preflight | Returns `204 No Content` |
| Rejected Preflight | Returns `403 Forbidden` when the custom checks fail |
| Allowed Origin Header | Returns `Access-Control-Allow-Origin` |
| Allowed Methods Header | Returns `Access-Control-Allow-Methods` |
| Allowed Headers Header | Returns `Access-Control-Allow-Headers` |
| Credentialed Requests | Configures `Access-Control-Allow-Credentials` |
| Preflight Caching | Configures `Access-Control-Max-Age` |
| Cache Variation | Uses `Vary` headers for relevant request values |

### Configured Origins

```python
ALLOWED_ORIGINS = {
    "http://127.0.0.1:5500",
}
```

Only the explicitly configured origin passes the middleware's origin check.

For example, `http://localhost:5500` and `http://127.0.0.1:5500` are different origins because their hostnames differ.

---

## 🛡️ CSRF Protection

The project keeps Django's CSRF middleware enabled and demonstrates how to obtain and submit a CSRF token for an unsafe request.

### CSRF Endpoint

```text
GET /api/csrf/
```

The endpoint uses Django's `get_token(request)` and `@ensure_csrf_cookie` to return a token and ensure that a CSRF cookie is set.

### Example Frontend Request

```javascript
const API_URL = "http://127.0.0.1:8000/api/";

const csrfResponse = await fetch(API_URL + "csrf/", {
    credentials: "include",
});

const csrfData = await csrfResponse.json();

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
```

The browser sends eligible cookies according to its cookie and credential policies. Django validates the CSRF information before allowing the unsafe request to proceed.

**Important:** The current `/api/` view returns welcome JSON for POST requests. It does not create or save a Laptop record in a database.

---

## 🧠 Important Concepts Practiced

### CORS and Browser Security

- Same-Origin Policy
- Cross-Origin Resource Sharing
- Origins: scheme, hostname, and port
- CORS request and response headers
- Simple requests and preflighted requests
- Credentialed cross-origin requests

### HTTP and Middleware

- HTTP methods: GET, POST, OPTIONS, PATCH, DELETE
- Request headers and response headers
- HTTP status codes: `200`, `204`, `403`
- Django middleware execution order
- Custom middleware and allowlist validation

### CSRF Protection

- Cross-Site Request Forgery
- CSRF cookies and tokens
- `X-CSRFToken`
- `get_token(request)`
- `@ensure_csrf_cookie`
- `CsrfViewMiddleware`
- `CSRF_TRUSTED_ORIGINS`

### Testing and Troubleshooting

- Browser Network tab
- Postman request configuration
- CORS preflight testing
- CSRF cookie and token validation
- Diagnosing `403 Forbidden`
- Separating CORS failures from CSRF failures

---

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/` | Returns the welcome JSON response |
| `POST` | `/api/` | Returns the welcome JSON when the request passes applicable middleware checks |
| `GET` | `/api/csrf/` | Returns a CSRF token and ensures a CSRF cookie is set |
| `OPTIONS` | `/api/` | Handles qualifying CORS preflight requests through the custom middleware |

### Example Welcome Response

```json
{
    "message": "Welcome to Django CORS Learning Lab!",
    "status": "success",
    "backend": "Django"
}
```

### Example CSRF Response

```json
{
    "csrfToken": "your-generated-csrf-token"
}
```

The actual token is generated by Django and will differ between requests.

---

## 🧪 Testing

The project uses both Postman and a web browser to investigate HTTP request behavior.

### Postman Testing

The following scenarios were tested:

- GET `/api/`
- GET `/api/csrf/`
- OPTIONS with an allowed origin
- OPTIONS with an unapproved origin
- POST with valid CSRF information
- POST without the required CSRF information

### Observed Results

| Test | Observed Result |
|---|---|
| GET `/api/` | `200 OK` |
| GET `/api/csrf/` | `200 OK` with a CSRF token |
| OPTIONS with configured origin and permitted request | `204 No Content` |
| OPTIONS with `http://localhost:5500` | `403 Forbidden` in our implementation |
| Initial POST without required CSRF information | `403 Forbidden` |
| POST after supplying valid CSRF information | `200 OK` |

These results describe the tested project behavior. Postman does not enforce browser CORS rules, so browser testing is also required.

### Browser Testing

The browser was used to verify:

- Automatic OPTIONS preflight behavior
- JavaScript Fetch API requests
- Cookie handling with `credentials: "include"`
- CSRF token submission
- Successful POST requests after the CSRF flow was corrected

---

## 📁 Project Structure

```text
django-cors-lab/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   └── api/
│       ├── views.py
│       ├── urls.py
│       └── middleware.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── docs/
│   ├── 01-project-architecture.md
│   ├── 02-cors-fundamentals.md
│   ├── 03-options-preflight-flow.md
│   ├── 04-csrf-protection-flow.md
│   └── 05-testing-and-troubleshooting.md
│
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

### Backend

- Python
- Django
- Django Middleware
- Django CSRF Protection

### Frontend

- HTML
- CSS
- JavaScript
- Fetch API

### API Testing

- Postman
- Browser Developer Tools

### Development Tools

- VS Code
- Git
- GitHub
- VS Code Live Server

---

## ⚙️ Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/django-cors-lab.git
cd django-cors-lab
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

```bash
cd backend
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

If you use Windows Command Prompt instead:

```bat
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Django

Ensure your Django settings contain the intended local development configuration, including:

```python
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]
```

Keep the allowed origin and CSRF trusted origin consistent with the frontend origin:

```python
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5500",
]
```

The Django secret key should be loaded from an environment variable rather than committed in source code. Do not upload your `.env` file or real credentials to GitHub.

### 5. Run Django System Checks

```bash
python manage.py check
```

### 6. Start the Backend

```bash
python manage.py runserver 127.0.0.1:8000
```

Backend URL:

```text
http://127.0.0.1:8000/api/
```

### 7. Start the Frontend

Open the `frontend` folder in VS Code and run `index.html` using Live Server on port `5500`.

Frontend URL:

```text
http://127.0.0.1:5500
```

Make sure `frontend/script.js` uses the correct backend URL.

---

## 📚 Documentation

The complete learning journey is organized into five focused documents.

| Document | Description |
|---|---|
| [01 — Project Architecture](docs/01-project-architecture.md) | Project structure, components, endpoints, and architecture |
| [02 — CORS Fundamentals](docs/02-cors-fundamentals.md) | Origins, same-origin policy, CORS headers, and credentials |
| [03 — OPTIONS Preflight Flow](docs/03-options-preflight-flow.md) | Browser preflight behavior and custom middleware validation |
| [04 — CSRF Protection Flow](docs/04-csrf-protection-flow.md) | CSRF cookies, tokens, middleware, and request validation |
| [05 — Testing and Troubleshooting](docs/05-testing-and-troubleshooting.md) | Test cases, expected results, common errors, and debugging |

---

## 🎓 Learning Outcomes

By building this project, I gained practical experience with:

- Understanding CORS beyond theory
- Identifying origins and same-origin restrictions
- Implementing custom Django middleware
- Understanding the browser's OPTIONS preflight lifecycle
- Validating requested methods and headers
- Understanding CORS response headers
- Understanding why CORS and CSRF are separate
- Obtaining and sending CSRF tokens
- Debugging CSRF cookie and token errors
- Testing HTTP requests using Postman
- Inspecting browser Network requests
- Understanding middleware execution order
- Documenting backend architecture and request flows
- Using Git and GitHub to manage a learning project

---

## 🧠 Final Mental Model

```text
                 FRONTEND
                     │
                     ▼
              BROWSER FETCH
                     │
                     ▼
             CORS PRELIGHT?
                     │
          ┌──────────┴──────────┐
          │                     │
       Rejected              Approved
          │                     │
          ▼                     ▼
    Browser Blocks        Actual Request
                                │
                                ▼
                      DJANGO CORS MIDDLEWARE
                                │
                                ▼
                       DJANGO CSRF CHECK
                                │
                     ┌──────────┴──────────┐
                     │                     │
                  Invalid                Valid
                     │                     │
                     ▼                     ▼
                403 Response           API VIEW
                                           │
                                           ▼
                                    JSON RESPONSE
```

The key idea is that **CORS and CSRF play different roles in the same request lifecycle**. A request may pass the CORS preflight and still fail Django's CSRF validation.

---

## 🚀 Project Scope

This is a learning project focused on understanding CORS and CSRF behavior in a Django application.

It uses custom CORS middleware to make the request lifecycle and policy checks visible. For production applications, evaluate a maintained CORS library such as `django-cors-headers` where appropriate, and configure it carefully alongside Django's existing security middleware.

This project does not implement user authentication, database-backed product creation, or a production deployment pipeline.

---

## ⭐ Key Takeaway

> The goal of this project was not simply to make a cross-origin request work. It was to understand how browser security, CORS preflight, Django middleware, CSRF tokens, and cookies interact throughout the complete request-to-response lifecycle.
