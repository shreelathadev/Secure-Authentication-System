import os
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_duplicate():
    resp = client.post("/api/v1/auth/register", json={
        "email": "test@example.com", "password": "Passw0rd1", "full_name": "Test User"
    })
    assert resp.status_code == 201
    resp2 = client.post("/api/v1/auth/register", json={
        "email": "test@example.com", "password": "Passw0rd1"
    })
    assert resp2.status_code == 400

def test_login_requires_verification():
    resp = client.post("/api/v1/auth/login", data={
        "username": "test@example.com", "password": "Passw0rd1"
    })
    assert resp.status_code == 403  # not verified yet