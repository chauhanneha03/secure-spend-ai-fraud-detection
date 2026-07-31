"""Smoke tests for the critical SecureSpend workflow."""

import importlib
import sys


def load_app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test_fraud_detection.db"))
    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    return module.app


def register(client):
    return client.post(
        "/register",
        data={
            "full_name": "Test Candidate",
            "email": "candidate@example.com",
            "username": "candidate",
            "password": "secure-password-123",
        },
        follow_redirects=True,
    )


def test_registration_login_and_risk_assessment(monkeypatch, tmp_path):
    app = load_app(monkeypatch, tmp_path)
    client = app.test_client()

    assert b"Account created" in register(client).data
    login = client.post("/login", data={"identity": "candidate", "password": "secure-password-123"}, follow_redirects=True)
    assert login.status_code == 200
    assert b"Good to see you" in login.data

    assessment = client.post(
        "/detect",
        data={
            "card_number": "5555 5555 5555 4444",
            "card_holder": "Test Candidate",
            "amount": "75000",
            "merchant": "International Electronics Store",
            "category": "Electronics",
            "transaction_type": "Online",
            "city": "Unknown City",
        },
        follow_redirects=True,
    )
    assert assessment.status_code == 200
    assert b"Review required" in assessment.data
    assert b"Fraud risk" in assessment.data
