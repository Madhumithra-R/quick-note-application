# 📝 QuickNotes — Secure Flask Notes Application

> **Internship Assignment — Task 1: Secure Web Application**  
> A lightweight, secure, and modern single-page-style personal notes manager built with Python and Flask.

---

## 📌 Project Overview

**QuickNotes** is a secure notes web application designed to demonstrate the complete HTTP request-response lifecycle, user session management, database persistence, and multi-tenant data isolation. Authenticated users can write, view, edit, search, and delete personal notes in real-time within an intuitive, responsive dashboard.

### 🌟 Key Features
- **Single-Page Application (SPA) Experience**: Interactive note creation, modal-based editing, deletion confirmation, and real-time live search without page reloads.
- **Strict Data Privacy**: Users can access and manage only their own notes. Any attempt to access another user's note returns `403 Forbidden`.
- **Modern UI**: Clean purple-and-white theme built with semantic HTML5, responsive CSS3, and vanilla JavaScript.
- **Enterprise-Grade Security**: Protection against CSRF, SQL Injection, XSS, brute-force attacks, and session hijacking.

---

## 🛠️ Technology Stack

Built strictly using standard, lightweight technologies without extra unnecessary frameworks:

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.12+ / Flask 3.0 | Application core & routing |
| **Database** | SQLite + Flask-SQLAlchemy | Relational database ORM |
| **Authentication** | Flask-Login + Werkzeug | User authentication & password hashing |
| **Security** | Flask-WTF + Flask-Limiter | CSRF token protection & rate limiting |
| **Templating** | Jinja2 | Dynamic HTML rendering with auto-escaping (XSS defense) |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive purple-and-white UI (No React/Node.js) |
| **Production WSGI** | Gunicorn | Production-ready HTTP WSGI server for cloud deployment |

---

## 🔐 Security Features

| Security Feature | Implementation Details |
| :--- | :--- |
| **Password Hashing** | Uses PBKDF2-SHA256 (`generate_password_hash(password, method='pbkdf2:sha256')`). |
| **Password Policy** | Minimum 8 characters, at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special symbol (`!@#$%^&*...`). |
| **Account Lockout** | Automatically locks the account for **5 minutes** after **3 consecutive failed login attempts**. |
| **CSRF Protection** | CSRF tokens enforced on all standard forms and AJAX JSON requests (`X-CSRFToken` header). |
| **Session Inactivity Timeout** | Sessions expire automatically after **20 minutes of inactivity** (`PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)`). |
| **Cookie Hardening** | `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`. |
| **Rate Limiting** | Rate-limited via Flask-Limiter: `5 per minute` on sensitive authentication endpoints (`/login`, `/sign-up`). |
| **SQL Injection Defense** | All database transactions use SQLAlchemy ORM parameterized queries. |
| **XSS Prevention** | Jinja2 auto-escapes user input by default to neutralize malicious `<script>` payloads. |

---

## 🗄️ Database Architecture

The application uses an SQLite database with two relational tables:

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

- Each user has a `1-to-many` relationship with `notes`.
- Deleting a user cascades and removes all associated notes (`cascade='all, delete-orphan'`).

---

## 📁 Project Structure

```
quick-note-application/
│
├── main.py                     # Application entry point
├── Procfile                    # Cloud deployment process file (Gunicorn)
├── requirements.txt            # Python dependencies
├── test_app.py                 # Automated test suite (7 comprehensive test cases)
├── README.md                   # Project documentation
│
└── website/
    ├── __init__.py             # App factory, extensions, and error handlers
    ├── auth.py                 # Authentication, lockout logic, and session control
    ├── views.py                # Notes dashboard, CRUD endpoints, and access checks
    ├── models.py               # User and Note SQLAlchemy models
    ├── forms.py                # WTForms definitions & password validation rules
    │
    ├── templates/
    │   ├── base.html           # Base layout, navbar, CSRF meta, alert messages
    │   ├── home.html           # Notes dashboard, search bar, creation card, modals
    │   ├── login.html          # Sign-in page with lockout warnings
    │   └── sign_up.html        # Sign-up page with real-time rule checklist
    │
    └── static/
        ├── style.css           # Modern purple-and-white responsive styling
        └── script.js           # Live search, char counter, and AJAX modal operations
```

---

## 🚀 Getting Started (Local Setup)

### Prerequisites
- Python 3.10 or higher installed on your computer.

### 1. Clone the Repository
```bash
git clone https://github.com/Madhumithra-R/quick-note-application.git
cd quick-note-application
```

### 2. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv ca2
.\ca2\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv ca2
source ca2/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Testing Guide

### Automated Test Suite
The project includes a comprehensive test suite in `test_app.py` that verifies all security and functional requirements.

To run the automated tests:
```powershell
python test_app.py
```

#### Test Coverage:
1. **User Registration**: Enforces email validation, duplicate prevention, and password rules.
2. **Password Hashing**: Confirms `pbkdf2:sha256` hashing algorithm.
3. **Login & Lockout**: Verifies 3 failed attempts trigger a 5-minute lockout and unlock correctly.
4. **Notes CRUD**: Validates note creation, editing, deletion, and chronological ordering.
5. **Cross-User Isolation**: Verifies User B cannot view, edit, or delete User A's notes (returns `403 Forbidden`).
6. **SQLi & XSS Protection**: Tests SQL injection immunity and Jinja2 script escaping.
7. **CSRF & Rate Limiting**: Tests CSRF token requirements and `429 Too Many Requests` responses.

---

## ☁️ Cloud Deployment (Render)

This application is ready for cloud deployment on **Render**:

1. Log in to [render.com](https://render.com) using your GitHub account.
2. Click **New +** &rarr; **Web Service**.
3. Connect your repository: `Madhumithra-R/quick-note-application`.
4. Configure service settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`
   - **Instance Type**: `Free`
5. Click **Deploy Web Service**.

---

## 📜 Acknowledgments

- Architectural foundation inspired by the open-source Flask tutorial by **Tech With Tim**.
- Custom-built and enhanced with enterprise security features for **Internship Task 1**.
