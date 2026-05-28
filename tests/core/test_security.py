import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


@pytest.mark.security
def test_hash_and_verify_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)


@pytest.mark.security
def test_verify_wrong_password():
    hashed = hash_password("secret123")
    assert not verify_password("wrong", hashed)


@pytest.mark.security
def test_create_access_token():
    token = create_access_token({"sub": "42"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


@pytest.mark.security
def test_create_refresh_token():
    token = create_refresh_token({"sub": "42"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


@pytest.mark.security
def test_decode_invalid_token():
    assert decode_token("not.a.token") is None
