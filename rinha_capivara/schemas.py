from pydantic import BaseModel, ConfigDict, constr, conint, Field


class ClientePublic(BaseModel):
    id: int
    saldo: int
    limite: int
    model_config = ConfigDict(from_attributes=True)


class ClienteList(BaseModel):
    clientes: list[ClientePublic]


class TransacaoSchema(BaseModel):
    valor: conint(ge=0)
    tipo: str = Field(pattern=r"[cd]")
    descricao: constr(min_length=1, max_length=10)


class SaldoCliente(BaseModel):
    limite: int
    saldo: int
