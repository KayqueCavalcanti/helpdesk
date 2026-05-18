from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user, require_admin
from ..database import get_db
from ..repositories.chamado_repository import ChamadoRepository
from ..repositories.comentario_repository import ComentarioRepository
from ..schemas import (
    ChamadoCreate,
    ChamadoListResponse,
    ChamadoResponse,
    ChamadoUpdate,
    ComentarioCreate,
    ComentarioResponse,
)

router = APIRouter(prefix="/api/chamados", tags=["chamados"])


@router.post("/", response_model=ChamadoListResponse, status_code=status.HTTP_201_CREATED)
def criar_chamado(
    payload: ChamadoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    return ChamadoRepository(db).create(
        titulo=payload.titulo, descricao=payload.descricao, autor_id=current_user.id
    )


@router.get("/", response_model=list[ChamadoListResponse])
def listar_chamados(
    status: Optional[models.StatusChamado] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    return ChamadoRepository(db).list_filtered(
        autor_id=None if current_user.is_admin else current_user.id,
        status=status,
        q=q,
    )


@router.get("/{chamado_id}", response_model=ChamadoResponse)
def detalhar_chamado(
    chamado_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    chamado = ChamadoRepository(db).find_by_id(chamado_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if not current_user.is_admin and chamado.autor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return chamado


@router.patch("/{chamado_id}/status", response_model=ChamadoListResponse)
def atualizar_status(
    chamado_id: int,
    payload: ChamadoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    chamado = ChamadoRepository(db).find_by_id(chamado_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return ChamadoRepository(db).update_status(chamado, payload.status)


@router.post("/{chamado_id}/comentarios", response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
def adicionar_comentario(
    chamado_id: int,
    payload: ComentarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    chamado = ChamadoRepository(db).find_by_id(chamado_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if not current_user.is_admin and chamado.autor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return ComentarioRepository(db).create(
        conteudo=payload.conteudo, chamado_id=chamado_id, autor_id=current_user.id
    )
