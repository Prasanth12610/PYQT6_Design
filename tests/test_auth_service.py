"""
tests/test_auth_service.py
--------------------------
Automated tests for services/auth_service.py and utils/security.py.
Run with:  pytest tests/ -v --cov=services --cov=utils
"""

import sys
import os

# Make project root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import hash_password, verify_password

# ── Security / hashing tests ──────────────────────────────────────────────────


class TestHashPassword:
    def test_produces_64_char_hex_digest(self):
        """SHA-256 hash must always be 64 hex characters."""
        result = hash_password("MySecret1!")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_is_not_plaintext(self):
        """Stored hash must never equal the original password."""
        pw = "PlainTextPassword"
        assert hash_password(pw) != pw

    def test_same_input_gives_same_hash(self):
        """Hashing is deterministic — same input, same output."""
        assert hash_password("hello") == hash_password("hello")

    def test_different_inputs_give_different_hashes(self):
        """Distinct passwords must produce distinct hashes."""
        assert hash_password("password1") != hash_password("password2")


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        """Correct password must verify successfully."""
        stored = hash_password("correct_pw")
        assert verify_password("correct_pw", stored) is True

    def test_wrong_password_returns_false(self):
        """Wrong password must fail verification."""
        stored = hash_password("real_password")
        assert verify_password("wrong_password", stored) is False

    def test_empty_password_does_not_crash(self):
        """Edge case: empty string should not raise an exception."""
        stored = hash_password("")
        assert verify_password("", stored) is True
        assert verify_password("notempty", stored) is False

    def test_case_sensitive(self):
        """Passwords are case-sensitive: 'Hello' ≠ 'hello'."""
        stored = hash_password("Hello")
        assert verify_password("hello", stored) is False
