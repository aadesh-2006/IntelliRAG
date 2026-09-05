import uuid
from datetime import timedelta
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models.user import User
from tests.conftest import TestingSessionLocal

def test_password_hashing_and_verification():
    plain = "SuperSecurePassword123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False

def test_jwt_generation_and_decoding():
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert "exp" in payload

def test_expired_jwt_rejected():
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-10))
    payload = decode_access_token(token)
    assert payload is None

def test_user_registration_success(client):
    payload = {
        "email": "analyst@intellirag.ai",
        "password": "SecurePassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "analyst@intellirag.ai"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data

def test_duplicate_user_registration_rejected(client):
    payload = {
        "email": "unique@intellirag.ai",
        "password": "SecurePassword123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_plaintext_password_never_stored():
    db = TestingSessionLocal()
    user = User(
        email="plaincheck@intellirag.ai",
        password_hash=hash_password("MyPlainPassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    fetched_user = db.query(User).filter(User.email == "plaincheck@intellirag.ai").first()
    assert fetched_user is not None
    assert fetched_user.password_hash != "MyPlainPassword123"
    assert verify_password("MyPlainPassword123", fetched_user.password_hash) is True
    db.close()

def test_user_login_oauth2_form_success(client):
    client.post("/api/auth/register", json={
        "email": "member@intellirag.ai",
        "password": "CorrectPassword123"
    })
    login_res = client.post("/api/auth/login", data={
        "username": "member@intellirag.ai",
        "password": "CorrectPassword123"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_user_login_invalid_password(client):
    client.post("/api/auth/register", json={
        "email": "member2@intellirag.ai",
        "password": "CorrectPassword123"
    })
    login_res = client.post("/api/auth/login", data={
        "username": "member2@intellirag.ai",
        "password": "WrongPassword456"
    })
    assert login_res.status_code == 401
    assert "Incorrect email or password" in login_res.json()["detail"]

def test_user_login_nonexistent_email(client):
    login_res = client.post("/api/auth/login", data={
        "username": "unknown@intellirag.ai",
        "password": "CorrectPassword123"
    })
    assert login_res.status_code == 401
    assert "Incorrect email or password" in login_res.json()["detail"]

def test_get_me_with_valid_jwt(client):
    reg_res = client.post("/api/auth/register", json={
        "email": "profile@intellirag.ai",
        "password": "SecurePassword123"
    })
    user_id = reg_res.json()["id"]

    login_res = client.post("/api/auth/login", data={
        "username": "profile@intellirag.ai",
        "password": "SecurePassword123"
    })
    token = login_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["id"] == user_id
    assert data["email"] == "profile@intellirag.ai"
    assert "password_hash" not in data

def test_get_me_without_jwt(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_get_me_with_malformed_jwt(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-valid-token"})
    assert response.status_code == 401