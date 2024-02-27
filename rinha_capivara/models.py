from enum import Enum

from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class TipoTransacao(str, Enum):
    c = 'c'
    d = 'd'


class Cliente(Base):
    __tablename__ = 'clientes'

    id: Mapped[int] = mapped_column(primary_key=True)
    saldo: Mapped[int] = mapped_column()
    limite: Mapped[int] = mapped_column()

    transacoes: Mapped[list["Transacao"]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan"
    )


class Transacao(Base):
    __tablename__ = 'transacoes'

    id: Mapped[int] = mapped_column(primary_key=True)
    valor: Mapped[int]
    tipo: Mapped[TipoTransacao]
    descricao: Mapped[str] = mapped_column(String(10))
    realizada_em: Mapped[datetime]
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    cliente: Mapped["Cliente"] = relationship(back_populates="transacoes")
