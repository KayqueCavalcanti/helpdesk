import enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class StatusChamado(str, enum.Enum):
    ABERTO = "Aberto"
    EM_ANDAMENTO = "Em Andamento"
    RESOLVIDO = "Resolvido"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    chamados = relationship("Chamado", back_populates="autor", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="autor")


class Chamado(Base):
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(String(2000), nullable=False)
    status = Column(SAEnum(StatusChamado), default=StatusChamado.ABERTO, nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    autor = relationship("Usuario", back_populates="chamados")
    comentarios = relationship(
        "Comentario",
        back_populates="chamado",
        cascade="all, delete-orphan",
        order_by="Comentario.criado_em",
    )


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    conteudo = Column(String(2000), nullable=False)
    chamado_id = Column(Integer, ForeignKey("chamados.id", ondelete="CASCADE"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    chamado = relationship("Chamado", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")
