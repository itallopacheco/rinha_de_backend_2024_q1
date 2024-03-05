BEGIN;
CREATE TABLE clientes (
    saldo INTEGER NOT NULL, 
    limite INTEGER NOT NULL, 
    id SERIAL NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TYPE tipotransacao AS ENUM ('c', 'd');

CREATE TABLE transacoes (
    valor INTEGER NOT NULL, 
    tipo tipotransacao NOT NULL, 
    descricao VARCHAR(10) NOT NULL, 
    id SERIAL NOT NULL, 
    realizada_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    cliente_id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(cliente_id) REFERENCES clientes (id)
);

ALTER TABLE transacoes ADD CONSTRAINT "transacao_cliente_id_fk" FOREIGN KEY (cliente_id) REFERENCES clientes (id);
CREATE INDEX IF NOT EXISTS  idx_cliente_id ON clientes(id);
CREATE INDEX IF NOT EXISTS idx_transacao_id_cliente_realizada_em_desc ON transacoes(cliente_id, realizada_em DESC);
CREATE EXTENSION IF NOT EXISTS pg_prewarm;
SELECT pg_prewarm('clientes');
SELECT pg_prewarm('transacoes');


CREATE OR REPLACE FUNCTION atualizar_saldo(cliente_id INT, tipo_transacao CHAR(1), valor_transacao NUMERIC,
                                           OUT text_msg TEXT, OUT is_error BOOLEAN, OUT updated_balance NUMERIC, OUT client_limit NUMERIC) AS $$
DECLARE
    client_record RECORD;
    limite_cliente NUMERIC;
    saldo_cliente NUMERIC;
    BEGIN
        SELECT * INTO client_record FROM clientes WHERE id = cliente_id FOR UPDATE; -- FOR UPDATE LOCKS
        IF NOT FOUND THEN -- early return
            text_msg := 'Cliente não encontrado.';
            is_error := TRUE;
            updated_balance := 0;
            client_limit := 0;
            RETURN ;
        END IF;

        limite_cliente := client_record.limite;
        IF tipo_transacao = 'c' THEN
            saldo_cliente := client_record.saldo + valor_transacao;
        ELSEIF tipo_transacao = 'd' THEN
            saldo_cliente := client_record.saldo - valor_transacao;
            IF limite_cliente + saldo_cliente < 0 THEN
                text_msg := 'Limite ultrapassado.';
                is_error := TRUE;
                updated_balance := 0;
                client_limit := 0;
                RETURN ;
            END IF;
        END IF;
        UPDATE clientes SET saldo = saldo_cliente WHERE id = cliente_id;
        text_msg := 'Saldo do Cliente atualizado com sucesso';
        is_error := FALSE;
        updated_balance := saldo_cliente;
        client_limit := limite_cliente;
END;
$$ LANGUAGE plpgsql;


INSERT INTO clientes (id, saldo, limite)
VALUES
    (1, 0, 100000),
    (2, 0, 80000),
    (3, 0, 1000000),
    (4, 0, 10000000),
    (5, 0, 500000);

COMMIT;