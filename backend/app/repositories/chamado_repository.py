from typing import Optional

from sqlalchemy.orm import Session

from .. import models


class ChamadoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, titulo: str, descricao: str, autor_id: int) -> models.Chamado:
        chamado = models.Chamado(titulo=titulo, descricao=descricao, autor_id=autor_id)
        self.db.add(chamado)
        self.db.commit()
        self.db.refresh(chamado)
        return chamado

    def find_by_id(self, chamado_id: int) -> models.Chamado | None:
        return self.db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()

    def list_filtered(
        self,
        autor_id: Optional[int] = None,
        status: Optional[models.StatusChamado] = None,
        q: Optional[str] = None,
    ) -> list[models.Chamado]:
        query = self.db.query(models.Chamado)
        if autor_id is not None:
            query = query.filter(models.Chamado.autor_id == autor_id)
        if status is not None:
            query = query.filter(models.Chamado.status == status)
        if q:
            term = f"%{q}%"
            query = query.filter(
                models.Chamado.titulo.ilike(term) | models.Chamado.descricao.ilike(term)
            )
        return query.order_by(models.Chamado.criado_em.desc()).all()

    def update_status(self, chamado: models.Chamado, status: models.StatusChamado) -> models.Chamado:
        chamado.status = status
        self.db.commit()
        self.db.refresh(chamado)
        return chamado
