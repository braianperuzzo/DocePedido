"""Testes da atualização aditiva dos campos de cupom em SQLite."""

import sqlite3

from aplicacao import criar_aplicacao


def test_base_anterior_ao_cupom_recebe_campos_sem_recriar_tabela(tmp_path):
    caminho = tmp_path / "legado-cupom.db"
    with sqlite3.connect(caminho) as conexao:
        conexao.execute(
            """
            CREATE TABLE detalhe_pedido (
                id INTEGER PRIMARY KEY,
                pedido_id INTEGER NOT NULL UNIQUE,
                tipo_entrega VARCHAR(30) NOT NULL,
                forma_pagamento VARCHAR(30) NOT NULL,
                valor_frete NUMERIC(10, 2) NOT NULL DEFAULT 0,
                endereco_entrega TEXT
            )
            """
        )

    aplicacao = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-legado-cupom",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{caminho}",
            "INICIALIZAR_DADOS": False,
        }
    )

    resposta = aplicacao.test_client().get("/")
    assert resposta.status_code == 200

    with sqlite3.connect(caminho) as conexao:
        colunas = {
            linha[1]: linha
            for linha in conexao.execute("PRAGMA table_info(detalhe_pedido)")
        }

    assert "cupom_codigo" in colunas
    assert "valor_desconto" in colunas
    assert str(colunas["valor_desconto"][4]) in {"0", "'0'", '"0"'}
