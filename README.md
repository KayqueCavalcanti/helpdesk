# WP Craft — Helpdesk

> Portal de Atendimento e Gestão de Chamados · Projeto de portfólio B2B

[![CI](https://github.com/KayqueCavalcanti/helpdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/KayqueCavalcanti/helpdesk/actions)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema completo de helpdesk com autenticação JWT, controle de acesso baseado em perfis (RBAC), fluxo de estados de chamados, threads de comentários e busca avançada.

---

## Funcionalidades

| Feature | Detalhe |
|---|---|
| **Autenticação JWT** | Tokens com expiração configurável, senhas com BCrypt |
| **RBAC** | Guards `get_current_user` e `require_admin` via FastAPI Depends |
| **Fluxo de estados** | `Aberto → Em Andamento → Resolvido` controlado por Admin |
| **Comentários** | Thread por chamado com autor e timestamp |
| **Busca e filtro** | Por status e texto livre (título + descrição) |
| **Repository Pattern** | Camada de dados desacoplada dos controllers |
| **Migrações** | Alembic para versionamento de schema |
| **Docker** | `docker-compose up` sobe o ambiente completo |
| **Testes** | pytest com 12+ casos cobrindo auth, RBAC e filtros |

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│                  Frontend (HTML / JS)                     │
│        Tailwind CDN · Fetch API · JWT localStorage       │
└───────────────────────────┬──────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼──────────────────────────────┐
│                 FastAPI  (Python 3.12)                    │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │ /api/auth   │  │  /api/chamados   │  │ CORS · JWT │  │
│  └──────┬──────┘  └────────┬─────────┘  └────────────┘  │
│         │                  │                              │
│  ┌──────▼──────────────────▼──────────┐                  │
│  │         Repository Layer            │                  │
│  │  UsuarioRepo · ChamadoRepo          │                  │
│  │  ComentarioRepo                     │                  │
│  └──────────────────┬─────────────────┘                  │
│                     │ SQLAlchemy ORM                      │
│  ┌──────────────────▼─────────────────┐                  │
│  │        SQLite  (Alembic)            │                  │
│  └─────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────┘
```

---

## Tech Stack

**Backend:** FastAPI · SQLAlchemy · Alembic · PyJWT · Passlib/BCrypt · python-dotenv  
**Banco:** SQLite (dev) — compatível com PostgreSQL via `DATABASE_URL`  
**Frontend:** HTML · Vanilla JS · Tailwind CSS (CDN)  
**DevOps:** Docker · GitHub Actions CI  
**Testes:** pytest · FastAPI TestClient

---

## Endpoints da API

### Auth
| Método | Rota | Acesso |
|---|---|---|
| `POST` | `/api/auth/registrar` | Público |
| `POST` | `/api/auth/login` | Público |
| `GET` | `/api/auth/me` | Autenticado |

### Chamados
| Método | Rota | Acesso |
|---|---|---|
| `POST` | `/api/chamados/` | Autenticado |
| `GET` | `/api/chamados/?status=&q=` | Autenticado |
| `GET` | `/api/chamados/{id}` | Dono ou Admin |
| `PATCH` | `/api/chamados/{id}/status` | **Admin only** |
| `POST` | `/api/chamados/{id}/comentarios` | Dono ou Admin |

Documentação interativa: `http://localhost:8001/api/docs`

---

## Como Rodar

### Com Docker (recomendado)

```bash
git clone https://github.com/KayqueCavalcanti/helpdesk
cd helpdesk
cp .env.example .env        # edite a SECRET_KEY
docker-compose up --build
```

Acesse `http://localhost:8001`

### Localmente

**Pré-requisito:** Python 3.12+

```bash
# 1. Clone
git clone https://github.com/KayqueCavalcanti/helpdesk
cd helpdesk

# 2. Ambiente virtual (Windows)
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Dependências
pip install -r backend/requirements.txt

# 4. Variáveis de ambiente
cp .env.example .env

# 5. Banco de dados
cd backend
alembic upgrade head

# 6. Servidor
uvicorn app.main:app --reload --port 8001
```

### Testes

```bash
pip install -r backend/requirements-dev.txt
cd backend
pytest tests/ -v
```

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | — | Chave JWT — **obrigatório** em produção |
| `ALGORITHM` | `HS256` | Algoritmo de assinatura |
| `ACCESS_TOKEN_EXPIRE_HOURS` | `24` | TTL do token em horas |
| `DATABASE_URL` | `sqlite:///./helpdesk.db` | URL do banco de dados |

Gere uma chave segura com:
```bash
openssl rand -hex 32
```

---

## Estrutura do Projeto

```
helpdesk/
├── .env.example
├── .github/
│   └── workflows/ci.yml        # GitHub Actions
├── docker-compose.yml
├── frontend/
│   ├── index.html              # Tela de login
│   └── painel.html             # Dashboard
└── backend/
    ├── alembic.ini
    ├── migrations/             # Alembic
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── tests/
    │   ├── test_auth.py
    │   └── test_chamados.py
    └── app/
        ├── auth.py             # JWT + guards
        ├── config.py           # Env vars
        ├── database.py         # Engine + session
        ├── main.py             # App entry point
        ├── models.py           # SQLAlchemy models
        ├── schemas.py          # Pydantic I/O
        ├── repositories/
        │   ├── usuario_repository.py
        │   ├── chamado_repository.py
        │   └── comentario_repository.py
        └── routers/
            ├── auth_router.py
            └── chamados_router.py
```

---

## Próximos Passos

- [ ] Notificações por e-mail (SMTP / SendGrid)
- [ ] Paginação nos endpoints de lista
- [ ] Dashboard com gráficos (Chart.js)
- [ ] Suporte a PostgreSQL em produção
- [ ] Upload de anexos nos chamados

---

Desenvolvido por **WP Craft** · Portfólio de soluções B2B
