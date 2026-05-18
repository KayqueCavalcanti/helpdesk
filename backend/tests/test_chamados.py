import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _criar_usuario(email="user@test.com", is_admin=False):
    db = SessionLocal()
    u = models.Usuario(nome="User", email=email, senha_hash=hash_password("senha123"), is_admin=is_admin)
    db.add(u)
    db.commit()
    db.refresh(u)
    db.close()
    return u


def _token(email="user@test.com"):
    return client.post("/api/auth/login", data={"username": email, "password": "senha123"}).json()["access_token"]


def _auth(email="user@test.com"):
    return {"Authorization": f"Bearer {_token(email)}"}


def test_criar_chamado():
    _criar_usuario()
    r = client.post("/api/chamados/", json={"titulo": "Meu Chamado", "descricao": "Descrição detalhada aqui"}, headers=_auth())
    assert r.status_code == 201
    assert r.json()["status"] == "Aberto"


def test_usuario_ve_apenas_seus_chamados():
    _criar_usuario("a@test.com")
    _criar_usuario("b@test.com")
    client.post("/api/chamados/", json={"titulo": "Chamado A", "descricao": "Descrição detalhada A"}, headers=_auth("a@test.com"))
    r = client.get("/api/chamados/", headers=_auth("b@test.com"))
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_admin_ve_todos_chamados():
    _criar_usuario("user@test.com")
    _criar_usuario("admin@test.com", is_admin=True)
    client.post("/api/chamados/", json={"titulo": "Chamado user", "descricao": "Descrição do usuário aqui"}, headers=_auth("user@test.com"))
    r = client.get("/api/chamados/", headers=_auth("admin@test.com"))
    assert len(r.json()) == 1


def test_alterar_status_requer_admin():
    _criar_usuario("user@test.com")
    _criar_usuario("admin@test.com", is_admin=True)
    cid = client.post("/api/chamados/", json={"titulo": "Chamado", "descricao": "Descrição aqui"}, headers=_auth("user@test.com")).json()["id"]

    r_user = client.patch(f"/api/chamados/{cid}/status", json={"status": "Em Andamento"}, headers=_auth("user@test.com"))
    assert r_user.status_code == 403

    r_admin = client.patch(f"/api/chamados/{cid}/status", json={"status": "Em Andamento"}, headers=_auth("admin@test.com"))
    assert r_admin.status_code == 200
    assert r_admin.json()["status"] == "Em Andamento"


def test_filtro_por_status():
    _criar_usuario("admin@test.com", is_admin=True)
    _criar_usuario("user@test.com")
    cid = client.post("/api/chamados/", json={"titulo": "Chamado", "descricao": "Descrição aqui"}, headers=_auth("user@test.com")).json()["id"]
    client.patch(f"/api/chamados/{cid}/status", json={"status": "Resolvido"}, headers=_auth("admin@test.com"))

    r_aberto = client.get("/api/chamados/?status=Aberto", headers=_auth("admin@test.com"))
    assert len(r_aberto.json()) == 0

    r_resolvido = client.get("/api/chamados/?status=Resolvido", headers=_auth("admin@test.com"))
    assert len(r_resolvido.json()) == 1


def test_filtro_por_texto():
    _criar_usuario()
    client.post("/api/chamados/", json={"titulo": "Erro no login", "descricao": "Usuário não consegue autenticar"}, headers=_auth())
    client.post("/api/chamados/", json={"titulo": "Tela em branco", "descricao": "Dashboard não carrega"}, headers=_auth())

    r = client.get("/api/chamados/?q=login", headers=_auth())
    assert len(r.json()) == 1
    assert "login" in r.json()[0]["titulo"].lower()


def test_adicionar_comentario():
    _criar_usuario()
    cid = client.post("/api/chamados/", json={"titulo": "Chamado", "descricao": "Descrição aqui"}, headers=_auth()).json()["id"]
    r = client.post(f"/api/chamados/{cid}/comentarios", json={"conteudo": "Estou verificando o problema"}, headers=_auth())
    assert r.status_code == 201
    assert r.json()["conteudo"] == "Estou verificando o problema"


def test_detalhar_chamado_inclui_comentarios():
    _criar_usuario()
    cid = client.post("/api/chamados/", json={"titulo": "Chamado", "descricao": "Descrição aqui"}, headers=_auth()).json()["id"]
    client.post(f"/api/chamados/{cid}/comentarios", json={"conteudo": "Primeiro comentário"}, headers=_auth())
    r = client.get(f"/api/chamados/{cid}", headers=_auth())
    assert r.status_code == 200
    assert len(r.json()["comentarios"]) == 1
