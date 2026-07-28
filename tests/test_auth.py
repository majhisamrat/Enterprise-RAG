import pytest
from app.utils.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing():
    pwd = "EnterpriseSecretPassword2026!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token():
    payload = {"sub": "12345", "org": "67890"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "12345"
    assert decoded["org"] == "67890"
