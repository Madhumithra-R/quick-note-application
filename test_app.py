import unittest
import os
from datetime import datetime, timedelta, timezone
from website import create_app, db, limiter
from website.models import User, Note
from werkzeug.security import check_password_hash

class SecureNotesAppTestCase(unittest.TestCase):
    def setUp(self):
        limiter.enabled = False
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['RATELIMIT_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        limiter.enabled = True
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration_and_password_requirements(self):
        """Verify registration validations and PBKDF2-SHA256 password hashing."""
        # 1. Weak password (missing uppercase)
        res = self.client.post('/sign-up', data={
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'password123!',
            'confirm_password': 'password123!'
        }, follow_redirects=True)
        self.assertIn(b'Password must contain at least one uppercase letter.', res.data)

        # 2. Weak password (missing special char)
        res_nospec = self.client.post('/sign-up', data={
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        self.assertIn(b'Password must contain at least one special character', res_nospec.data)

        # 3. Valid registration
        valid_pass = 'Secur3!P@ss'
        res_valid = self.client.post('/sign-up', data={
            'username': 'tester_valid',
            'email': 'tester@example.com',
            'password': valid_pass,
            'confirm_password': valid_pass
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully!', res_valid.data)

        # Verify password hash uses PBKDF2-SHA256
        with self.app.app_context():
            user = User.query.filter_by(email='tester@example.com').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.password_hash.startswith('pbkdf2:sha256'))
            self.assertTrue(check_password_hash(user.password_hash, valid_pass))

        # 4. Duplicate email prevention
        res_dup_email = self.client.post('/sign-up', data={
            'username': 'another_tester',
            'email': 'tester@example.com',
            'password': valid_pass,
            'confirm_password': valid_pass
        }, follow_redirects=True)
        self.assertIn(b'An account with this email already exists.', res_dup_email.data)

        # 5. Duplicate username prevention
        res_dup_user = self.client.post('/sign-up', data={
            'username': 'tester_valid',
            'email': 'different@example.com',
            'password': valid_pass,
            'confirm_password': valid_pass
        }, follow_redirects=True)
        self.assertIn(b'This username is already taken.', res_dup_user.data)

    def test_login_logout_and_account_lockout(self):
        """Verify login, 3-attempt lockout, 5-minute duration, and logout."""
        valid_pass = 'Secur3!P@ss'
        self.client.post('/sign-up', data={
            'username': 'lock_test',
            'email': 'lock@example.com',
            'password': valid_pass,
            'confirm_password': valid_pass
        }, follow_redirects=True)

        # Attempt 1: Failed password
        res1 = self.client.post('/login', data={'email': 'lock@example.com', 'password': 'WrongPassword1!'}, follow_redirects=True)
        self.assertIn(b'2 attempt(s) remaining before account lockout', res1.data)

        # Attempt 2: Failed password
        res2 = self.client.post('/login', data={'email': 'lock@example.com', 'password': 'WrongPassword2!'}, follow_redirects=True)
        self.assertIn(b'1 attempt(s) remaining before account lockout', res2.data)

        # Attempt 3: Failed password triggers 5-minute lockout
        res3 = self.client.post('/login', data={'email': 'lock@example.com', 'password': 'WrongPassword3!'}, follow_redirects=True)
        self.assertIn(b'Account locked! You have failed 3 consecutive login attempts', res3.data)

        with self.app.app_context():
            u = User.query.filter_by(email='lock@example.com').first()
            self.assertIsNotNone(u.locked_until)
            self.assertTrue(u.is_locked())

        # Attempt 4: Even with correct password, login is blocked while locked
        res4 = self.client.post('/login', data={'email': 'lock@example.com', 'password': valid_pass}, follow_redirects=True)
        self.assertIn(b'Your account is locked due to 3 consecutive failed login attempts', res4.data)

        # Test lockout expiration after 5 minutes
        with self.app.app_context():
            u = User.query.filter_by(email='lock@example.com').first()
            u.locked_until = datetime.now(timezone.utc) - timedelta(seconds=1)
            db.session.commit()

        # Login now succeeds with valid password
        res5 = self.client.post('/login', data={'email': 'lock@example.com', 'password': valid_pass}, follow_redirects=True)
        self.assertIn(b'Logged in successfully!', res5.data)

        # Test logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out successfully.', res_logout.data)

    def test_note_crud_and_user_isolation(self):
        """Verify note creation, viewing, editing, deletion, and cross-user isolation."""
        # Register and Login User A
        self.client.post('/sign-up', data={
            'username': 'user_a',
            'email': 'usera@example.com',
            'password': 'Secur3!P@ss',
            'confirm_password': 'Secur3!P@ss'
        }, follow_redirects=True)
        self.client.post('/login', data={'email': 'usera@example.com', 'password': 'Secur3!P@ss'}, follow_redirects=True)

        # Create note
        res_note = self.client.post('/', data={'content': 'User A First Private Note'}, follow_redirects=True)
        self.assertIn(b'Note created successfully!', res_note.data)
        self.assertIn(b'User A First Private Note', res_note.data)

        with self.app.app_context():
            note_a = Note.query.filter_by(content='User A First Private Note').first()
            self.assertIsNotNone(note_a)
            note_a_id = note_a.id

        # Edit note
        res_edit = self.client.post('/edit-note', json={'noteId': note_a_id, 'content': 'User A Updated Note'})
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn('Note updated successfully!', res_edit.get_json()['message'])

        # Verify update in DB
        with self.app.app_context():
            updated_note = db.session.get(Note, note_a_id)
            self.assertEqual(updated_note.content, 'User A Updated Note')

        # Logout User A
        self.client.get('/logout', follow_redirects=True)

        # Register and Login User B
        self.client.post('/sign-up', data={
            'username': 'user_b',
            'email': 'userb@example.com',
            'password': 'Secur3!P@ss',
            'confirm_password': 'Secur3!P@ss'
        }, follow_redirects=True)
        self.client.post('/login', data={'email': 'userb@example.com', 'password': 'Secur3!P@ss'}, follow_redirects=True)

        # User B dashboard should NOT display User A's note
        dash_b = self.client.get('/')
        self.assertNotIn(b'User A Updated Note', dash_b.data)

        # User B attempts to edit User A's note -> 403 Forbidden
        res_b_edit = self.client.post('/edit-note', json={'noteId': note_a_id, 'content': 'Hacked by B'})
        self.assertEqual(res_b_edit.status_code, 403)

        # User B attempts to delete User A's note -> 403 Forbidden
        res_b_del = self.client.post('/delete-note', json={'noteId': note_a_id})
        self.assertEqual(res_b_del.status_code, 403)

        # Logout User B and Login User A to delete their own note
        self.client.get('/logout', follow_redirects=True)
        self.client.post('/login', data={'email': 'usera@example.com', 'password': 'Secur3!P@ss'}, follow_redirects=True)

        res_del = self.client.post('/delete-note', json={'noteId': note_a_id})
        self.assertEqual(res_del.status_code, 200)

        with self.app.app_context():
            self.assertIsNone(db.session.get(Note, note_a_id))

    def test_sql_injection_and_xss_protection(self):
        """Verify SQL injection prevention and XSS output escaping."""
        # SQL injection attempt in login
        res_sqli = self.client.post('/login', data={
            'email': "' OR '1'='1' --",
            'password': "' OR '1'='1' --"
        }, follow_redirects=True)
        # Should cleanly reject because email format or user not found, without syntax error
        self.assertNotIn(b'sqlite3.OperationalError', res_sqli.data)
        self.assertIn(b'Please enter a valid email address.', res_sqli.data)

        # Register user and post XSS script payload
        valid_pass = 'Secur3!P@ss'
        self.client.post('/sign-up', data={
            'username': 'xss_tester',
            'email': 'xss@example.com',
            'password': valid_pass,
            'confirm_password': valid_pass
        }, follow_redirects=True)
        self.client.post('/login', data={'email': 'xss@example.com', 'password': valid_pass}, follow_redirects=True)

        xss_payload = "<script>alert('pwned')</script>"
        res_xss = self.client.post('/', data={'content': xss_payload}, follow_redirects=True)
        # Raw unescaped script tag must NOT be rendered; it must be HTML-escaped by Jinja2
        self.assertNotIn(b"<script>alert('pwned')</script>", res_xss.data)
        self.assertIn(b"&lt;script&gt;alert(&#39;pwned&#39;)&lt;/script&gt;", res_xss.data)

    def test_session_and_security_configuration(self):
        """Verify 20-minute inactivity timeout, HttpOnly, and SameSite Lax configuration."""
        self.assertEqual(self.app.config['PERMANENT_SESSION_LIFETIME'], timedelta(minutes=20))
        self.assertTrue(self.app.config['SESSION_COOKIE_HTTPONLY'])
        self.assertEqual(self.app.config['SESSION_COOKIE_SAMESITE'], 'Lax')

    def test_csrf_protection_enabled(self):
        """Verify CSRF token requirement for state-changing requests."""
        csrf_app = create_app()
        csrf_app.config['TESTING'] = True
        csrf_app.config['WTF_CSRF_ENABLED'] = True
        csrf_app.config['RATELIMIT_ENABLED'] = False
        csrf_client = csrf_app.test_client()

        # POST without CSRF token must fail with 400 Bad Request
        res = csrf_client.post('/sign-up', data={
            'username': 'nocsrf',
            'email': 'nocsrf@example.com',
            'password': 'Secur3!P@ss',
            'confirm_password': 'Secur3!P@ss'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'CSRF token is missing', res.data)

    def test_rate_limiting(self):
        """Verify rate limiting triggers 429 after exceeding limit."""
        limiter.enabled = True
        rate_app = create_app()
        rate_app.config['TESTING'] = True
        rate_app.config['WTF_CSRF_ENABLED'] = False
        rate_client = rate_app.test_client()

        status_codes = []
        for i in range(8):
            res = rate_client.post('/login', data={'email': 'rate@example.com', 'password': 'P@ss1234'}, follow_redirects=True)
            status_codes.append(res.status_code)

        self.assertIn(429, status_codes)

if __name__ == '__main__':
    unittest.main()
