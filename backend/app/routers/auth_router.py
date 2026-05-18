from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models
from ..auth import create_access_token, get_current_user, verify_password
from ..database import get_db
from ..repositories.usuario_repository import UsuarioRepository
from ..schemas import TokenResponse, UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(payload: UsuarioCreate, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    if repo.find_by_email(payload.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    return repo.create(nome=payload.nome, email=payload.email, senha=payload.senha)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    usuario = repo.find_by_email(form.username)
    if not usuario or not verify_password(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    token = create_access_token({"sub": str(usuario.id), "is_admin": usuario.is_admin})
    return TokenResponse(access_token=token, usuario=usuario)


@router.get("/me", response_model=UsuarioResponse)
def me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user
