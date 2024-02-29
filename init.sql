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
CREATE INDEX "transacao_clientE_id_id_idx" ON transacoes (cliente_id, "id");

INSERT INTO clientes (id, saldo, limite)
VALUES
    (1, 0, 100000),
    (2, 0, 80000),
    (3, 0, 1000000),
    (4, 0, 10000000),
    (5, 0, 500000);

COMMIT;