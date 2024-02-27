from datetime import datetime

from pydantic import BaseModel, ConfigDict, constr, conint, Field


class ClientePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    saldo: int
    limite: int


class TransacaoPublic(BaseModel):
    valor: conint(ge=0)
    tipo: str = Field(pattern=r"[cd]")
    descricao: constr(min_length=1, max_length=10)
    realizada_em: datetime


class ClienteList(BaseModel):
    clientes: list[ClientePublic]


class TransacaoSchema(BaseModel):
    valor: conint(ge=0)
    tipo: str = Field(pattern=r"[cd]")
    descricao: constr(min_length=1, max_length=10)
    realizada_em: datetime


class SaldoCliente(BaseModel):
    limite: int
    saldo: int


class SaldoClienteExtrato(BaseModel):
    total: int
    data_extrato: datetime
    limite: int


class Extrato(BaseModel):
    saldo: SaldoClienteExtrato
    ultimas_transacoes: list[TransacaoPublic] = []
