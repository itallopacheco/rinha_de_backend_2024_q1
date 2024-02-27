import datetime

from typing import Annotated
from sqlalchemy import select
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from rinha_capivara.database import get_session
from rinha_capivara.models import Cliente, Transacao, TipoTransacao
from rinha_capivara.schemas import TransacaoSchema, SaldoCliente, SaldoClienteExtrato, Extrato, TransacaoPublic

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
def fazer_transacao(cliente_id: int, transacao: TransacaoSchema, session: Session):
    #TODO: verificar se o paciente pode fazer a transacao

    """
    Regras Uma transação de débito nunca pode deixar o saldo do cliente menor que seu limite disponível.
    Por exemplo, um cliente com limite de 1000 (R$ 10) nunca deverá ter o saldo menor que -1000 (R$ -10).
     Nesse caso, um saldo de -1001 ou menor significa inconsistência na Rinha de Backend!

     # Se uma requisição para débito for deixar o saldo inconsistente, a API deve retornar HTTP Status Code 422
     sem completar a transação! O corpo da resposta nesse caso não será testado e você pode escolher como o representar.

     Se o atributo [id] da URL for de uma identificação não existente de cliente, a API deve retornar HTTP Status Code 404.
     O corpo da resposta nesse caso não será testado e você pode escolher como o representar.
    """

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

    saldo_resposta = SaldoCliente(limite=cliente.limite, saldo=cliente.saldo)
    session.add(transacao)
    session.commit()
    return saldo_resposta


@app.get('/clientes/{id_usuario}/extrato')
def get_cliente_extrato(id_usuario: int, session: Session):
    cliente = session.scalar(select(Cliente).where(Cliente.id == id_usuario))

    if not cliente:
        raise HTTPException(status_code=404, detail='Cliente não encontrado.')

    saldo = SaldoClienteExtrato(
        total=cliente.saldo,
        data_extrato=datetime.datetime.utcnow(),
        limite=cliente.limite,
    )
    ultimas_transacoes = []
    query = (
        session.query(Transacao)
        .join(Cliente)
        .filter(Cliente.id == id_usuario)
        .order_by(Transacao.realizada_em.desc())
        .limit(10)
    )
    results = query.all()
    for result in results:
        transacao = TransacaoPublic(
            valor=result.valor,
            tipo=result.tipo,
            descricao=result.descricao,
            realizada_em=result.realizada_em
        )
        ultimas_transacoes.append(transacao)
    return Extrato(
        saldo=saldo,
        ultimas_transacoes=ultimas_transacoes
    )
