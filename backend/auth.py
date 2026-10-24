import os
import re
import streamlit as st
from supabase import create_client

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _secret(name):
    """Read a setting from environment variables first, then Streamlit Secrets."""
    if os.getenv(name):
        return os.getenv(name)
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return None


def auth_configured():
    return bool(_secret("SUPABASE_URL") and _secret("SUPABASE_KEY"))


def _sb():
    """One Supabase client PER visitor session. Sharing a client between visitors would leak logins."""
    if "sb_client" not in st.session_state:
        st.session_state.sb_client = create_client(_secret("SUPABASE_URL"), _secret("SUPABASE_KEY"))
    return st.session_state.sb_client


def db():
    """The signed-in visitor's client, with a fresh login token (used for the library)."""
    sb = _sb()
    try:
        sb.auth.get_session()  # refreshes the token if it has expired
    except Exception:
        pass
    return sb


def _friendly(e):
    msg = str(getattr(e, "message", None) or e).lower()
    if "invalid login" in msg:
        return "Wrong email or password."
    if "already registered" in msg or "already been registered" in msg:
        return "An account with this email already exists. Try signing in."
    if "password" in msg and ("least" in msg or "weak" in msg):
        return "That password is too weak. Use at least 8 characters."
    if "rate limit" in msg or "too many" in msg:
        return "Too many attempts. Wait a few minutes and try again."
    if "not confirmed" in msg:
        return "This email isn't confirmed yet. Ask the app owner to turn off email confirmation, or check your inbox."
    return "Couldn't complete that. Please try again."


def _user_dict(user, fallback_name=""):
    meta = getattr(user, "user_metadata", None) or {}
    return {
        "id": user.id,
        "email": user.email,
        "name": meta.get("display_name") or fallback_name or "Student",
    }


def sign_up(email, password, name):
    """Returns (user_dict, None) on success or (None, message) on failure."""
    try:
        res = _sb().auth.sign_up(
            {"email": email, "password": password, "options": {"data": {"display_name": name}}}
        )
    except Exception as e:
        return None, _friendly(e)
    if res.user is None:
        return None, "Couldn't create the account. Please try again."
    if res.session is None:
        return None, "Account created. Check your email to confirm it, then sign in."
    return _user_dict(res.user, name), None


def sign_in(email, password):
    """Returns (user_dict, None) on success or (None, message) on failure."""
    try:
        res = _sb().auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        return None, _friendly(e)
    if res.user is None:
        return None, "Couldn't sign in. Please try again."
    return _user_dict(res.user), None


def sign_out():
    try:
        _sb().auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("sb_client", None)
