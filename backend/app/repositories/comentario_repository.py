from sqlalchemy.orm import Session

from .. import models


class ComentarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, conteudo: str, chamado_id: int, autor_id: int) -> models.Comentario:
        comentario = models.Comentario(
            conteudo=conteudo,
            chamado_id=chamado_id,
            autor_id=autor_id,
        )
        self.db.add(comentario)
        self.db.commit()
        self.db.refresh(comentario)
        return comentario

    def list_by_chamado(self, chamado_id: int) -> list[models.Comentario]:
        return (
            self.db.query(models.Comentario)
            .filter(models.Comentario.chamado_id == chamado_id)
            .order_by(models.Comentario.criado_em)
            .all()
        )
