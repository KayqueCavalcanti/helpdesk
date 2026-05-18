from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .database import Base, engine
from .routers import auth_router, chamados_router

_frontend = Path(__file__).parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="WP Craft Helpdesk",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(chamados_router.router)


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(str(_frontend / "index.html"))


@app.get("/painel.html", include_in_schema=False)
async def serve_painel():
    return FileResponse(str(_frontend / "painel.html"))
