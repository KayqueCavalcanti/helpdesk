<h1 align="center">🎫 Central de Ajuda</h1>

<p align="center">
  <strong>Sistema de Helpdesk com Autenticação JWT e Controle de Acesso por Perfis</strong><br/>
  Portfólio técnico para vaga de Desenvolvedor(a) Backend Júnior — APIs REST, Autenticação e Regras de Negócio
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-produção-4169E1?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/Alembic-migrations-6BA81E" />
  <img src="https://img.shields.io/badge/JWT-auth-000000?logo=jsonwebtokens&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-containerizado-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white" />
</p>

<p align="center">
  <a href="https://central-de-ajuda-blni.onrender.com"><strong>🔗 Demo ao vivo</strong></a>
  &nbsp;·&nbsp;
  <a href="https://central-de-ajuda-blni.onrender.com/api/docs"><strong>📖 Documentação da API (Swagger)</strong></a>
</p>

> ⏱️ **Nota sobre a demo:** hospedada no plano gratuito do Render. Após um período de inatividade, o primeiro acesso pode levar ~50 segundos para "acordar" o servidor. É um ambiente de demonstração — os dados podem ser resetados periodicamente.

---

## Índice

1. [Sobre o Projeto](#sobre-o-projeto)
2. [Demo e Credenciais de Teste](#demo-e-credenciais-de-teste)
3. [Arquitetura](#arquitetura)
4. [Controle de Acesso (RBAC)](#controle-de-acesso-rbac)
5. [Estrutura de Diretórios](#estrutura-de-diretórios)
6. [API Reference](#api-reference)
7. [Como Executar](#como-executar)
8. [Testes](#testes)
9. [Pipeline CI](#pipeline-ci)
10. [Stack Tecnológico](#stack-tecnológico)
11. [Decisões Técnicas e Tradeoffs](#decisões-técnicas-e-tradeoffs)
12. [Próximos Passos](#próximos-passos)

---

## Sobre o Projeto

A **Central de Ajuda** é uma API REST full-stack construída em Python/FastAPI que implementa um sistema de helpdesk completo, com autenticação, autorização por perfis e um ciclo de vida de chamados. O projeto foi desenhado para demonstrar o "feijão-com-arroz" de backend feito com rigor: autenticação segura, separação de responsabilidades e regras de acesso bem definidas.

| Módulo | Responsabilidade |
|---|---|
| **Autenticação** | Registro e login com senha protegida via `bcrypt`. Emite tokens JWT assinados com expiração configurável. Endpoint `/me` para recuperar o usuário autenticado |
| **Controle de Acesso** | Dois perfis (usuário comum e administrador). Cada endpoint valida permissões: um usuário só enxerga e comenta os próprios chamados; o admin enxerga todos e é o único que altera status |
| **Chamados** | Ciclo de vida completo: abertura, listagem filtrada por perfil, detalhamento, transição de status (`Aberto` → `Em Andamento` → `Resolvido`) e threads de comentários |

O código aplica **arquitetura em camadas** (routers → repositories → models), **injeção de dependência** nativa do FastAPI e **migrations versionadas** com Alembic, com uma cobertura de testes que valida tanto a autenticação quanto as regras de acesso.

---

## Demo e Credenciais de Teste

A aplicação está publicada e pode ser testada diretamente:

- **Interface:** https://central-de-ajuda-blni.onrender.com
- **API / Swagger:** https://central-de-ajuda-blni.onrender.com/api/docs

Para explorar rapidamente, registre um usuário na própria tela de login ou use a documentação interativa do Swagger para testar cada endpoint.

> **Dica:** o primeiro usuário registrado é um usuário comum. Para testar os recursos de administrador (ver todos os chamados, alterar status), consulte a seção de configuração de admin no código ou promova um usuário via banco de dados.

---

## Arquitetura

A aplicação segue uma **arquitetura em camadas**, com separação rígida de responsabilidades. As rotas não contêm lógica de acesso a dados — elas delegam para repositórios, que encapsulam as consultas.

```
╔══════════════════════════════════════════════════════════════════════╗
║                     CAMADA DE APRESENTAÇÃO (Routers)                 ║
║  POST /api/auth/registrar     POST /api/auth/login    GET /api/auth/me║
║  POST /api/chamados           GET  /api/chamados      PATCH .../status║
║  auth_router.py               chamados_router.py                      ║
╚══════════════════════════════╤═══════════════════════════════════════╝
                               │  Depends() injeta usuário autenticado
╔══════════════════════════════▼═══════════════════════════════════════╗
║                   CAMADA DE AUTENTICAÇÃO / SEGURANÇA                 ║
║  hash_password / verify_password (bcrypt)                            ║
║  create_access_token / get_current_user (JWT)                        ║
║  require_admin  ← guard de autorização por perfil                    ║
╚══════════════════════════════╤═══════════════════════════════════════╝
                               │  Trabalha com objetos de domínio
╔══════════════════════════════▼═══════════════════════════════════════╗
║                   CAMADA DE REPOSITÓRIO (Data Access)               ║
║  UsuarioRepository     ChamadoRepository     ComentarioRepository    ║
║  Encapsula todas as queries SQLAlchemy — as rotas não fazem SQL      ║
╚══════════════════════════════╤═══════════════════════════════════════╝
                               │  Mapeia objetos ↔ tabelas
╔══════════════════════════════▼═══════════════════════════════════════╗
║                   CAMADA DE INFRAESTRUTURA                           ║
║  models.py (ORM)      Alembic migrations      PostgreSQL / SQLite     ║
║  Usuario · Chamado · Comentario · StatusChamado (Enum)               ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Por que essa arquitetura?**
- Os **routers** são adaptadores HTTP finos: validam entrada (Pydantic), injetam o usuário autenticado via `Depends()` e delegam para os repositórios
- Os **repositórios** centralizam o acesso ao banco — trocar a lógica de uma query não exige tocar nas rotas
- A **camada de segurança** é reutilizável: qualquer rota que precise de proteção só declara `Depends(get_current_user)` ou `Depends(require_admin)`

---

## Controle de Acesso (RBAC)

O sistema implementa autorização baseada em perfil de forma explícita e testada. A regra central: **um usuário comum só acessa os próprios recursos; o administrador acessa todos.**

| Ação | Usuário comum | Administrador |
|---|---|---|
| Registrar / Login | ✅ | ✅ |
| Abrir chamado | ✅ | ✅ |
| Listar chamados | 🔒 Apenas os próprios | ✅ Todos |
| Ver detalhe de um chamado | 🔒 Apenas os próprios (`403` caso contrário) | ✅ Qualquer um |
| Comentar em um chamado | 🔒 Apenas nos próprios | ✅ Em qualquer um |
| Alterar status do chamado | ❌ `403 Forbidden` | ✅ Exclusivo do admin |

```python
# A autorização é declarativa. Alterar status exige perfil admin:
@router.patch("/{chamado_id}/status")
def atualizar_status(
    ...,
    current_user: models.Usuario = Depends(require_admin),  # guard de perfil
):
    ...

# E o filtro de listagem respeita o perfil sem duplicar código:
return ChamadoRepository(db).list_filtered(
    autor_id=None if current_user.is_admin else current_user.id,
)
```

---

## Estrutura de Diretórios

```
Atendimento/
├── backend/
│   ├── app/
│   │   ├── main.py                  ← App Factory FastAPI, CORS, serve o frontend
│   │   ├── config.py                ← Variáveis de ambiente (SECRET_KEY, DATABASE_URL)
│   │   ├── database.py              ← Engine e sessão SQLAlchemy
│   │   ├── models.py                ← ORM: Usuario, Chamado, Comentario
│   │   ├── schemas.py               ← Schemas Pydantic (validação de entrada/saída)
│   │   ├── auth.py                  ← JWT, bcrypt, get_current_user, require_admin
│   │   ├── routers/
│   │   │   ├── auth_router.py       ← /api/auth/*
│   │   │   └── chamados_router.py   ← /api/chamados/*
│   │   └── repositories/
│   │       ├── usuario_repository.py
│   │       ├── chamado_repository.py
│   │       └── comentario_repository.py
│   ├── migrations/                  ← Alembic (versionamento de schema)
│   ├── tests/
│   │   ├── test_auth.py             ← Testes de registro, login e token
│   │   └── test_chamados.py         ← Testes de CRUD e regras de acesso
│   ├── Dockerfile                   ← python:3.12-slim, roda migrations no start
│   └── requirements.txt
│
├── frontend/
│   ├── index.html                   ← Portal de login (Vanilla JS + Fetch API)
│   └── painel.html                  ← Painel de chamados
│
├── .github/workflows/ci.yml         ← Pipeline: instala deps → roda pytest
├── docker-compose.yml               ← Ambiente local (build + volume + env)
├── render.yaml                      ← Blueprint de deploy (web service + PostgreSQL)
└── .env.example                     ← Modelo de variáveis de ambiente
```

---

## API Reference

Base URL da demo: `https://central-de-ajuda-blni.onrender.com`

### `POST /api/auth/registrar`

Cria um novo usuário. A senha é armazenada como hash `bcrypt`, nunca em texto puro.

**Corpo:**
```json
{ "nome": "Maria Silva", "email": "maria@exemplo.com", "senha": "senha123" }
```
**Resposta `201 Created`:** dados do usuário (sem a senha).

---

### `POST /api/auth/login`

Autentica e retorna um token JWT. Segue o padrão OAuth2 (`username` = email, `password` = senha).

**Resposta `200 OK`:**
```json
{ "access_token": "eyJhbGciOiJIUzI1NiI...", "token_type": "bearer" }
```

---

### `GET /api/auth/me`

Retorna o usuário autenticado. Requer header `Authorization: Bearer <token>`.

---

### `POST /api/chamados`

Abre um novo chamado, associado automaticamente ao usuário autenticado.

**Corpo:**
```json
{ "titulo": "Sistema fora do ar", "descricao": "Não consigo acessar o painel." }
```

---

### `GET /api/chamados`

Lista chamados. **Usuário comum** recebe apenas os próprios; **admin** recebe todos.

---

### `GET /api/chamados/{id}`

Detalha um chamado com sua thread de comentários. Retorna `403` se um usuário comum tentar acessar um chamado que não é seu.

---

### `PATCH /api/chamados/{id}/status`

Altera o status do chamado (`Aberto` / `Em Andamento` / `Resolvido`). **Exclusivo de administradores** — retorna `403 Forbidden` para usuários comuns.

**Corpo:**
```json
{ "status": "Em Andamento" }
```

---

### `POST /api/chamados/{id}/comentarios`

Adiciona um comentário à thread. Respeita a mesma regra de acesso do detalhamento.

---

## Como Executar

### Pré-requisitos

- Python 3.12+ **ou** Docker
- Git

---

### Opção 1 — Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd Atendimento

# 2. Crie o arquivo .env a partir do modelo
cp .env.example .env
# gere um SECRET_KEY seguro:
#   openssl rand -hex 32
# e cole no .env

# 3. Suba o ambiente
docker compose up --build
```

Acesse **http://localhost:8001** e a documentação em **http://localhost:8001/api/docs**

---

### Opção 2 — Ambiente Local

```bash
cd backend

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Dependências
pip install -r requirements.txt

# Migrations e execução
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

> Por padrão, o ambiente local usa **SQLite** (`helpdesk.db`) — zero configuração de banco externo. Em produção, basta definir `DATABASE_URL` apontando para um PostgreSQL.

---

## Testes

```bash
cd backend

# Todos os testes com saída detalhada
pytest tests/ -v

# Instale as dependências de desenvolvimento antes, se necessário:
pip install -r requirements-dev.txt
```

### Estratégia de Testes

| Técnica | Aplicada em | Por quê |
|---|---|---|
| **Banco isolado por teste** | `test_auth.py`, `test_chamados.py` | Cada suíte parte de um banco limpo, garantindo determinismo |
| **Teste de fluxo de autenticação** | `test_auth.py` | Valida registro → login → acesso a rota protegida com o token emitido |
| **Teste das regras de acesso** | `test_chamados.py` | Verifica que usuário comum recebe `403` ao acessar recurso alheio ou tentar alterar status |

---

## Pipeline CI

O arquivo `.github/workflows/ci.yml` roda automaticamente a cada `push` e Pull Request nas branches `main` e `develop`:

```
┌─────────────────────────────────────────────────────────┐
│  git push / Pull Request (main, develop)                │
└───────────────────┬─────────────────────────────────────┘
                    │
          ┌─────────▼──────────┐
          │  Setup Python 3.12 │  com cache de pip
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  Install deps      │  requirements.txt + requirements-dev.txt
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  pytest            │  roda a suíte de testes com SQLite de CI
          └────────────────────┘
```

O CI usa um `SECRET_KEY` e um `DATABASE_URL` de teste próprios, isolados de qualquer credencial real — garantindo que a suíte rode de forma reproduzível em qualquer máquina.

---

## Stack Tecnológico

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| Backend | **Python** | 3.12 | Tipagem, dataclasses, ecossistema maduro para APIs |
| Framework web | **FastAPI** | 0.115 | Performance, injeção de dependência nativa, docs automáticas (Swagger) |
| ORM | **SQLAlchemy** | 2.0 | ORM padrão de mercado, sintaxe moderna 2.0 |
| Migrations | **Alembic** | 1.13 | Versionamento de schema — evolução segura do banco |
| Banco (produção) | **PostgreSQL** | — | Banco relacional robusto, adequado a múltiplos acessos |
| Banco (local) | **SQLite** | — | Zero setup para desenvolvimento e testes |
| Autenticação | **PyJWT + passlib/bcrypt** | — | Padrão de mercado para JWT e hashing seguro de senhas |
| Validação | **Pydantic** | 2.x | Validação declarativa de entrada e saída |
| Containerização | **Docker + Compose** | — | Ambiente reproduzível |
| CI | **GitHub Actions** | — | Pipeline nativo ao GitHub, roda testes a cada push |
| Deploy | **Render** | — | Deploy via Blueprint (`render.yaml`) com PostgreSQL gerenciado |
| Frontend | **HTML + CSS + Fetch API** | — | Zero frameworks — foco no backend |

---

## Decisões Técnicas e Tradeoffs

### SQLite (local) vs PostgreSQL (produção)

O projeto roda com **SQLite** localmente (zero configuração) e **PostgreSQL** em produção. A troca é transparente: o código lê a `DATABASE_URL` do ambiente e ajusta a conexão automaticamente.

| | SQLite (local) | PostgreSQL (produção) |
|---|---|---|
| **Setup** | Arquivo único, zero deps | Servidor gerenciado |
| **Concorrência** | Limitada | Múltiplos acessos simultâneos |
| **Persistência no Render** | Não persiste (disco efêmero) | Persiste em serviço dedicado |

> **Consequência prática:** o `database.py` aplica o argumento `check_same_thread` apenas quando a URL é SQLite, e o `config.py` normaliza o prefixo `postgres://` → `postgresql://` que alguns provedores fornecem. Isso torna o mesmo código portável entre os dois ambientes.

### CORS aberto (`allow_origins=["*"]`)

Durante o desenvolvimento e a demonstração, o CORS está aberto para facilitar testes. **Em produção real**, isso seria restringido à origem específica do frontend — um tradeoff consciente entre conveniência de portfólio e rigor de produção.

### Serve o frontend pelo próprio FastAPI

O mesmo serviço FastAPI serve a API e os arquivos estáticos do frontend. **Vantagem:** um único deploy, uma única URL, mais simples de demonstrar. **Limitação:** em um cenário de escala, front e back seriam separados (CDN para o front, API dedicada) — mas para um projeto de portfólio, a simplicidade compensa.

---

## Próximos Passos

Itens que demonstrariam maturidade adicional em uma evolução do projeto:

- [ ] **Refresh tokens** — hoje o token expira e exige novo login; um fluxo de refresh melhoraria a UX
- [ ] **Restringir CORS** à origem do frontend em produção via variável de ambiente
- [ ] **Paginação** na listagem de chamados — essencial conforme o volume cresce
- [ ] **Rate limiting** nos endpoints de autenticação — proteção contra força bruta
- [ ] **Testes de integração** com um PostgreSQL efêmero no CI (via service container do GitHub Actions)
- [ ] **Seed de admin** automatizado — criar um usuário administrador na primeira execução via variável de ambiente

---

## Autor

Desenvolvido como projeto de portfólio para demonstrar aplicação prática de:
- API REST com FastAPI e injeção de dependência
- Autenticação JWT e hashing seguro de senhas com bcrypt
- Autorização baseada em perfis (RBAC) validada por testes
- Arquitetura em camadas com padrão Repository
- Migrations versionadas com Alembic
- Containerização com Docker e deploy em produção (Render + PostgreSQL)
- Pipeline de CI com GitHub Actions

---

<p align="center">
  Construído com Python, FastAPI e atenção às regras que fazem um sistema confiável.
</p>
