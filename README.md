# 📝 QuickNotes

A secure and responsive notes application built with **Python, Flask, and SQLite**. Users can register, log in, and manage their personal notes through a simple dashboard.

## ✨ Features

- User registration and secure login
- Create, edit, delete, and search notes
- Live search without page reload
- AJAX-based note operations
- Password hashing and account lockout
- CSRF protection and rate limiting
- Automatic session expiration
- User-specific data privacy
- Responsive purple-and-white UI

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug
- **Security:** Flask-WTF, Flask-Limiter
- **Frontend:** HTML, CSS, JavaScript, Jinja2
- **Deployment:** Gunicorn, Render

## 📁 Project Structure

```text
quick-note-application/
│
├── main.py
├── requirements.txt
├── Procfile
├── test_app.py
│
└── website/
    ├── __init__.py
    ├── auth.py
    ├── views.py
    ├── models.py
    ├── forms.py
    ├── templates/
    └── static/
```

## 🚀 Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/Madhumithra-R/quick-note-application.git
cd quick-note-application
```

**2. Create and activate virtual environment**

```powershell
python -m venv ca2
.\ca2\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Start the application**

```bash
python main.py
```

Open: `http://127.0.0.1:5000`

## 🧪 Run Tests

```bash
python test_app.py
```

## 🔒 Security

- PBKDF2-SHA256 password hashing
- 3 failed login attempts trigger a 5-minute lockout
- 20-minute session timeout
- CSRF protection
- SQL injection prevention
- XSS protection
- HTTPOnly and SameSite cookies
- User-level data authorization

---

**Developed by Madhumithra R.**
