from sqlalchemy.orm import Session

from .. import models
from ..auth import hash_password


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str) -> models.Usuario | None:
        return self.db.query(models.Usuario).filter(models.Usuario.email == email).first()

    def find_by_id(self, user_id: int) -> models.Usuario | None:
        return self.db.query(models.Usuario).filter(models.Usuario.id == user_id).first()

    def create(self, nome: str, email: str, senha: str, is_admin: bool = False) -> models.Usuario:
        usuario = models.Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            is_admin=is_admin,
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def list_all(self) -> list[models.Usuario]:
        return self.db.query(models.Usuario).all()
