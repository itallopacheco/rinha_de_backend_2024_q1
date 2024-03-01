import datetime
import logging
from typing import Annotated

import sqlalchemy
from sqlalchemy import select, desc
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from rinha_capivara.database import get_async_session
from rinha_capivara.models import Cliente, Transacao, TipoTransacao
from rinha_capivara.schemas import SaldoCliente, SaldoClienteExtrato, Extrato, TransacaoPublic, \
    TransacaoReq

app = FastAPI()

AsyncSession = Annotated[AsyncSession, Depends(get_async_session)]


@app.get('/')
def health():
    return {'message': 'oi asmfdoasid !'}


@app.post('/clientes/{cliente_id}/transacoes')
async def fazer_transacao(cliente_id: int, transacao: TransacaoReq, session: AsyncSession):
    async with session.begin():

        resultado = await session.execute(
            sqlalchemy.text(
                "SELECT * FROM atualizar_saldo(:cliente_id, :tipo_transacao, :valor_transacao)"
            ),
            {
                "cliente_id": cliente_id,
                "tipo_transacao": transacao.tipo,
                "valor_transacao": transacao.valor
            }
        )

        text_msg, is_error, saldo_atualizado, limite_cliente = resultado.fetchone()
        # text_msg_str = str(text_msg)
        # is_error_str = str(is_error)
        saldo_atualizado_long = int(saldo_atualizado)
        limite_cliente_long = int(limite_cliente)

        if is_error:
            if text_msg == 'Cliente não encontrado.':
                raise HTTPException(status_code=404)
            if text_msg == 'Limite ultrapassado.':
                raise HTTPException(status_code=422)

        nova_transacao = Transacao(
            valor=transacao.valor,
            tipo=transacao.tipo,
            descricao=transacao.descricao,
            cliente_id=cliente_id,
            realizada_em=datetime.datetime.utcnow()
        )

        session.add(nova_transacao)
        await session.commit()

        saldo_cliente = SaldoCliente(
            limite = limite_cliente_long,
            saldo = saldo_atualizado_long
        )

    return saldo_cliente


@app.get('/clientes/{cliente_id}/extrato')
async def get_cliente_extrato(cliente_id: int, session: AsyncSession):
    async with session.begin():
        cliente_result = await session.execute(select(Cliente).where(Cliente.id == cliente_id))
        cliente = cliente_result.scalar()

        if not cliente:
            raise HTTPException(status_code=404, detail='Cliente não encontrado.')

        saldo = SaldoClienteExtrato(
            total=cliente.saldo,
            data_extrato=datetime.datetime.utcnow(),
            limite=cliente.limite,
        )
        ultimas_transacoes = []
        query = (
            select(Transacao)
            .join(Cliente)
            .filter(Cliente.id == cliente_id)
            .order_by(Transacao.realizada_em.desc())
            .limit(10)
        )
        results = await session.execute(query)
        for result in results.scalars():
            transacao = TransacaoPublic(
                valor=result.valor,
                tipo=result.tipo,
                descricao=result.descricao,
                realizada_em=result.realizada_em
            )
            ultimas_transacoes.append(transacao)
        extrato = Extrato(
            saldo=saldo,
            ultimas_transacoes=ultimas_transacoes
        )
    return extrato
