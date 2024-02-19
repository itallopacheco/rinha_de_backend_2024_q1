import datetime

from typing import Annotated
from sqlalchemy import select
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from rinha_capivara.database import get_session
from rinha_capivara.models import Cliente, Transacao, TipoTransacao
from rinha_capivara.schemas import TransacaoSchema, SaldoCliente

app = FastAPI()

Session = Annotated[Session, Depends(get_session)]


@app.get('/')
def health():
    return {'message': 'oi asmfdoasid !'}


@app.get('/clientes')
def get_clientes(session: Session, skip: int = 0, limit: int = 100):
    clientes = session.scalars(select(Cliente).offset(skip).limit(limit)).all()
    return {'clientes': clientes}


@app.post('/clientes/{cliente_id}/transacoes')
def fazer_transacao(cliente_id: int, transacao: TransacaoSchema, session:Session):
    cliente = session.scalar(select(Cliente).where(Cliente.id == cliente_id))

    if not cliente:
        raise HTTPException(status_code=404, detail='Cliente não encontrado.')

    saldo_cliente = cliente.saldo + cliente.limite
    if transacao.tipo == TipoTransacao.d and saldo_cliente < transacao.valor:
        raise HTTPException(status_code=422, detail='Saldo insuficiente.')

    transacao = Transacao(
        valor=transacao.valor,
        tipo=transacao.tipo,
        descricao=transacao.descricao,
        cliente_id=cliente_id,
        realizada_em=datetime.datetime.utcnow()
    )

    if transacao.tipo == TipoTransacao.c:
        cliente.saldo += transacao.valor
    if transacao.tipo == TipoTransacao.d:
        cliente.saldo -= transacao.valor

    saldo_resposta = SaldoCliente(limite=cliente.limite
                                  , saldo=cliente.saldo)
    session.add(transacao)
    session.commit()
    return saldo_resposta

