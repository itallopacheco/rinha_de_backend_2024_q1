import datetime
from typing import Annotated

import sqlalchemy
from sqlalchemy import select, desc
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from rinha_capivara.database import get_db
from rinha_capivara.models import Cliente, Transacao, TipoTransacao
from rinha_capivara.schemas import SaldoCliente, SaldoClienteExtrato, Extrato, TransacaoPublic, \
    TransacaoReq

app = FastAPI()


@app.get('/')
def health():
    return {'message': 'oi asmfdoasid !'}


@app.post('/clientes/{cliente_id}/transacoes')
def fazer_transacao(cliente_id: int, transacao: TransacaoReq, db: Session = Depends(get_db)):
    with db as session:
        resultado = session.execute(
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
        session.commit()

        saldo_cliente = SaldoCliente(
            limite=limite_cliente_long,
            saldo=saldo_atualizado_long
        )

    return saldo_cliente


@app.get('/clientes/{cliente_id}/extrato')
def get_cliente_extrato(cliente_id: int, db: Session = Depends(get_db)):
    with db as session:
        cliente_result = session.execute(
            sqlalchemy.text(
                "SELECT clientes.saldo, clientes.limite FROM clientes WHERE clientes.id = :cliente_id"
            ),
            {'cliente_id': cliente_id}

        )
        cliente = cliente_result.fetchone()

        if not cliente:
            raise HTTPException(status_code=404, detail='Cliente não encontrado.')

        saldo = SaldoClienteExtrato(
            total=cliente[0],
            data_extrato=datetime.datetime.utcnow(),
            limite=cliente[1],
        )

        ultimas_transacoes = []

        transacoes_result = session.execute(
            sqlalchemy.text(
                """
                    SELECT 
                        transacoes.valor,
                        transacoes.tipo,
                        transacoes.descricao,
                        transacoes.realizada_em,
                        clientes.saldo,
                        clientes.limite
                    FROM transacoes
                    JOIN 
                        clientes ON clientes.id = transacoes.cliente_id
                    WHERE 
                        clientes.id = :cliente_id
                    ORDER BY 
                        transacoes.realizada_em DESC
                    LIMIT 10
                """
            ),
            {'cliente_id': cliente_id}

        )
        results = transacoes_result.fetchall()
        for result in results:
            transacao = TransacaoPublic(
                valor=result[0],
                tipo=result[1],
                descricao=result[2],
                realizada_em=result[3]
            )
            ultimas_transacoes.append(transacao)
        extrato = Extrato(
            saldo=saldo,
            ultimas_transacoes=ultimas_transacoes
        )
    return extrato
