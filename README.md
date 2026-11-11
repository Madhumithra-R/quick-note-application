# Internship Task 1: Secure Flask Quick Note Application

A secure, single-page-style personal notes web application built with **Python** and **Flask**. This project enhances foundational Flask architecture concepts with robust enterprise-grade security practices, modern UI design, and multi-tenant data isolation.

---

## 1. Project Overview

QuickNotes provides a clean, responsive web interface where authenticated users can write, view, edit, search, and delete personal notes in real time. All notes are saved to an underlying SQLite database via SQLAlchemy ORM and isolated strictly to the creating user.

### Key Highlights
- **Single-Page Application (SPA) Experience**: Interactive note creation, in-place modal editing, deletion confirmation, and real-time live search without page reloads.
- **Strict Data Isolation**: Users can only access and manage their own notes. Any cross-tenant access attempts are rejected with `403 Forbidden`.
- **Modern UI**: Polished purple-and-white theme built purely with semantic HTML5, modern CSS3 (Flexbox/Grid), and vanilla JavaScript.
- **Security-First Architecture**: Implements CSRF tokens on all requests, PBKDF2-SHA256 hashing, rate limiting, 3-attempt account lockout, and 20-minute inactivity session expiry.

---

## 2. Technology Stack

In strict accordance with the internship assignment requirements, **only** standard, lightweight technologies were used:

- **Backend**: Python 3.12+, Flask 3.0+
- **Database**: SQLite (via Flask-SQLAlchemy ORM)
- **Authentication**: Flask-Login, Werkzeug Security
- **Security & Forms**: Flask-WTF (CSRF Protection), Flask-Limiter (Rate Limiting)
- **Templating**: Jinja2 (Automatic XSS Escaping)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (No React, Node.js, external JS frameworks, or third-party CSS libraries)

---

## 3. Security Implementation Details

| Security Feature | Implementation Mechanism |
| :--- | :--- |
| **CSRF Protection** | Enforced across all forms via `Flask-WTF` (`CSRFProtect`). JavaScript AJAX requests include dynamic `X-CSRFToken` headers. |
| **Password Hashing** | Uses PBKDF2-SHA256 (`generate_password_hash(password, method='pbkdf2:sha256')`). |
| **Password Policy** | Enforces minimum 8 characters, at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character (`[!@#$%^&*...]`). |
| **Account Lockout** | After **3 consecutive failed login attempts**, the account is locked for **5 minutes**. Valid logins reset failed attempts to 0. |
| **Session Inactivity Timeout** | Session lifetime is configured to **20 minutes** (`PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)`). Sessions are marked permanent and refreshed on active requests. |
| **Session Cookie Hardening** | `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`. |
| **Rate Limiting** | Configured via `Flask-Limiter` with an in-memory backend. Global limit (`200/day`, `50/hour`) and strict route limit (`5/minute`) on `/login` and `/sign-up`. |
| **SQL Injection Prevention** | All database interactions utilize SQLAlchemy ORM parameterized queries. Raw unescaped SQL strings are avoided. |
| **XSS Protection** | Jinja2 autoescaping is active on all templates; user content is treated strictly as plain text. |
| **Input Validation** | Form-level validation with WTForms (`DataRequired`, `Email`, `Length`, regex checks) and content trimming. |

---

## 4. Database Schema

SQLite database (`database.db`) consists of two relational tables:

```
+------------------------------------+          +------------------------------------+
|               users                |          |               notes                |
+------------------------------------+          +------------------------------------+
| id (INTEGER, PK)                   | 1      * | id (INTEGER, PK)                   |
| username (VARCHAR(150), UNIQUE)    |<-------->| content (TEXT)                     |
| email (VARCHAR(150), UNIQUE)       |          | created_at (DATETIME)              |
| password_hash (VARCHAR(256))       |          | updated_at (DATETIME)              |
| failed_login_attempts (INTEGER)    |          | user_id (INTEGER, FK -> users.id)  |
| locked_until (DATETIME, NULLABLE)  |          +------------------------------------+
+------------------------------------+
```

- **User**: Implements `UserMixin` for Flask-Login compatibility.
- **Relationship**: `users.notes` has a one-to-many relationship with cascade deletion (`cascade='all, delete-orphan'`).

---

## 5. Project Directory Structure

```
Quick note application/
│
├── main.py                    # Application entry point
├── requirements.txt           # Project dependencies
├── test_app.py                # Automated test suite (7 comprehensive test cases)
├── README.md                  # Complete documentation
│
└── website/
    ├── __init__.py            # App factory, configuration, extensions & error handlers
    ├── auth.py                # Registration, login, lockout logic, logout
    ├── views.py               # Notes dashboard, CRUD routes, authorization checks
    ├── models.py              # User and Note SQLAlchemy models
    ├── forms.py               # WTForms definitions & password policy validators
    │
    ├── templates/
    │   ├── base.html          # Base layout, navbar, CSRF meta, flash messages
    │   ├── home.html          # Notes dashboard, search bar, creation box, modals
    │   ├── login.html         # Login page with lockout notice
    │   └── sign_up.html       # Sign-up page with dynamic rule validation hints
    │
    └── static/
        ├── style.css          # Modern purple-and-white theme & responsive styles
        └── script.js          # SPA interactions: search, character counter, AJAX modals
```

---

## 6. Installation & Execution Guide

Follow these steps in Windows PowerShell:

### Step 1: Create Virtual Environment
```powershell
python -m venv ca2
```

### Step 2: Activate the Virtual Environment
```powershell
.\ca2\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
```powershell
python main.py
```

### Step 5: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 7. Running the Automated Test Suite

To verify all security requirements, authentication flows, and data isolation:

```powershell
.\ca2\Scripts\python.exe test_app.py
```

### Automated Test Coverage:
1. **User Registration**: Enforces email validation, duplicate prevention, and password complexity.
2. **Password Hashing**: Confirms `pbkdf2:sha256` hashing algorithm.
3. **Login & Lockout**: Verifies 3 failed attempts lock account for 5 minutes, and subsequent unlock.
4. **Notes CRUD**: Validates note creation, editing, deletion, and ordering (newest first).
5. **Cross-User Isolation**: Confirms User B cannot view, edit, or delete User A's notes (403 Forbidden).
6. **SQL Injection & XSS Protection**: Verifies SQL injection resistance and Jinja2 HTML escaping.
7. **CSRF & Rate Limiting**: Validates CSRF token enforcement and HTTP 429 response on rate exhaustion.

---

## 8. Acknowledgments

- **Inspiration**: Concept and architectural inspiration adapted from the open-source tutorial by **Tech With Tim** ([Flask Web App Tutorial](https://github.com/techwithtim/Flask-Web-App-Tutorial)).
- **Customization**: Engineered as a specialized, secure internal application for **Internship Task 1**, with comprehensive enhancements including custom WTForms validation, account lockout protection, rate limiting, and an upgraded SPA-style user interface.
