import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

client = TestClient(app)

PAYLOAD = {"nome": "Teste", "email": "teste@test.com", "senha": "senha123"}


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_registrar_usuario():
    r = client.post("/api/auth/registrar", json=PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == PAYLOAD["email"]
    assert data["is_admin"] is False


def test_registrar_email_duplicado():
    client.post("/api/auth/registrar", json=PAYLOAD)
    r = client.post("/api/auth/registrar", json=PAYLOAD)
    assert r.status_code == 400


def test_login_sucesso():
    client.post("/api/auth/registrar", json=PAYLOAD)
    r = client.post("/api/auth/login", data={"username": PAYLOAD["email"], "password": PAYLOAD["senha"]})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_senha_errada():
    client.post("/api/auth/registrar", json=PAYLOAD)
    r = client.post("/api/auth/login", data={"username": PAYLOAD["email"], "password": "errada"})
    assert r.status_code == 401


def test_me_retorna_usuario_autenticado():
    client.post("/api/auth/registrar", json=PAYLOAD)
    token = client.post("/api/auth/login", data={"username": PAYLOAD["email"], "password": PAYLOAD["senha"]}).json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == PAYLOAD["email"]


def test_me_sem_token():
    r = client.get("/api/auth/me")
    assert r.status_code == 401
