from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from .models import StatusChamado


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6)


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    is_admin: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class ComentarioCreate(BaseModel):
    conteudo: str = Field(..., min_length=1, max_length=2000)


class ComentarioResponse(BaseModel):
    id: int
    conteudo: str
    autor: UsuarioResponse
    criado_em: datetime

    model_config = {"from_attributes": True}


class ChamadoCreate(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=255)
    descricao: str = Field(..., min_length=10, max_length=2000)


class ChamadoUpdate(BaseModel):
    status: StatusChamado


class ChamadoListResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    status: StatusChamado
    autor: UsuarioResponse
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class ChamadoResponse(ChamadoListResponse):
    comentarios: list[ComentarioResponse] = []
