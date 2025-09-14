# modules/auth.py
from __future__ import annotations
import re, os, sqlite3, hashlib, hmac, secrets, time
from pathlib import Path
import streamlit as st

DB_PATH = Path("data/auth.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Email: simple regex
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Password: 8+ alphanumeric only
PASS_RE = re.compile(r"^[A-Za-z0-9]{8,}$")

# ---------- DB ----------
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash BLOB NOT NULL,
            salt BLOB NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    return conn

# ---------- Validation ----------
def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))

def validate_password_policy(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Password cannot be empty."
    if not PASS_RE.match(password):
        return False, "Password must be 8+ characters, alphanumeric only (no special characters)."
    return True, ""

def password_strength(password: str) -> tuple[int, str]:
    if not password:
        return 0, "Empty"
    score = 0
    n = len(password)
    # length contribution
    score += min(max(n - 8, 0), 12) * (50 // 12)
    # variety (since only alnum allowed)
    if re.search(r"[a-z]", password): score += 15
    if re.search(r"[A-Z]", password): score += 15
    if re.search(r"[0-9]", password): score += 20
    score = max(0, min(score, 100))
    label = "Weak"
    if score >= 70: label = "Strong"
    elif score >= 40: label = "Fair"
    return score, label

# ---------- Password Hash ----------
def _hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000, dklen=32)
    return dk, salt

# ---------- User Functions ----------
def signup_user(email: str, name: str, password: str) -> tuple[bool, str]:
    if not validate_email(email):
        return False, "❌ Please enter a valid email address."
    ok, msg = validate_password_policy(password)
    if not ok:
        return False, f"❌ {msg}"
    if not name or not name.strip():
        return False, "❌ Please enter your name."

    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email.lower(),))
    if cur.fetchone():
        return False, "❌ An account with this email already exists."

    pwhash, salt = _hash_password(password)
    cur.execute(
        "INSERT INTO users (email, name, password_hash, salt, created_at) VALUES (?,?,?,?,?)",
        (email.lower(), name.strip(), pwhash, salt, time.time())
    )
    conn.commit()
    return True, "✅ Account created successfully."

def signin_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    if not validate_email(email):
        return False, "❌ Invalid email format.", None
    ok, msg = validate_password_policy(password)
    if not ok:
        return False, f"❌ {msg}", None

    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT email, name, password_hash, salt FROM users WHERE email = ?", (email.lower(),))
    row = cur.fetchone()
    if not row:
        return False, "❌ No account found for this email.", None

    _, name, pwhash, salt = row
    calc, _ = _hash_password(password, salt)
    if not hmac.compare_digest(calc, pwhash):
        return False, "❌ Incorrect password.", None

    user = {"email": email.lower(), "name": name}
    return True, "✅ Signed in successfully.", user

# ---------- Session Helpers ----------
def ensure_session_keys():
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None

def current_user() -> dict | None:
    ensure_session_keys()
    return st.session_state.get("auth_user")

def require_login(message: str = "Please sign in or sign up to view this page.", show_forms: bool = True):
    ensure_session_keys()
    if st.session_state["auth_user"] is None:
        st.warning(message)
        if show_forms:
            mode = st.segmented_control("Mode", options=["Sign In", "Sign Up"], default="Sign In")
            if mode == "Sign In":
                login_form()
            else:
                signup_form()
        st.stop()
def gate_page(page_title: str = "This page requires an account", message: str = "Please sign in or sign up to view this page."):
    st.title(page_title)
    require_login(message=message, show_forms=True)

# ---------- UI ----------
def login_form():
    st.subheader("Sign in")
    email = st.text_input("Email", key="login_email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", key="login_password")
    if password:
        score, label = password_strength(password)
        st.progress(score, text=f"Password strength: {label} ({score})")
    if st.button("Sign In", type="primary"):
        ok, msg, user = signin_user(email, password)
        if ok:
            st.session_state["auth_user"] = user
            st.success(f"Welcome back, {user['name']}!")
            st.rerun()
        else:
            st.error(msg)

def signup_form():
    st.subheader("Create an account")
    name = st.text_input("Full name", key="signup_name", placeholder="Your name")
    email = st.text_input("Email (will be your username)", key="signup_email", placeholder="you@example.com")
    password = st.text_input("Password (8+ alphanumeric, no symbols)", type="password", key="signup_password")
    if password:
        score, label = password_strength(password)
        st.progress(score, text=f"Password strength: {label} ({score})")
    if st.button("Sign Up", type="primary"):
        ok, msg = signup_user(email, name, password)
        if ok:
            st.success("Account created! Please sign in.")
        else:
            st.error(msg)

def logout_button():
    user = current_user()
    if user:
        if st.button("Log out"):
            st.session_state["auth_user"] = None
            st.success("Logged out.")
            st.rerun()

def user_greeting():
    user = current_user()
    if user:
        st.info(f"👋 Hello, **{user['name']}** ({user['email']})")
