"""Testes de compatibilidade com bancos SQLite criados antes do campo CPF."""

import sqlite3

from werkzeug.security import generate_password_hash

from aplicacao import criar_aplicacao


def test_base_legada_recebe_cpf_sem_apagar_cliente(tmp_path):
    """Atualiza a tabela antiga na primeira requisição e preserva seus registros."""
    caminho = tmp_path / "legado.db"
    with sqlite3.connect(caminho) as conexao:
        conexao.execute(
            """
            CREATE TABLE cliente (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                senha_hash VARCHAR(255) NOT NULL,
                telefone VARCHAR(20),
                ativo BOOLEAN NOT NULL DEFAULT 1,
                data_cadastro DATETIME NOT NULL
            )
            """
        )
        conexao.execute(
            """
            INSERT INTO cliente
                (nome, email, senha_hash, telefone, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Cliente Legado",
                "legado@example.com",
                generate_password_hash("Legado@123"),
                None,
                1,
                "2026-08-01 12:00:00",
            ),
        )

    aplicacao = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-legado",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{caminho}",
            "INICIALIZAR_DADOS": False,
        }
    )

    with sqlite3.connect(caminho) as conexao:
        antes = {linha[1] for linha in conexao.execute("PRAGMA table_info(cliente)")}
    assert "cpf" not in antes

    resposta = aplicacao.test_client().post(
        "/login",
        data={"email": "legado@example.com", "senha": "Legado@123"},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Bem-vindo, Cliente Legado" in resposta.text
    with sqlite3.connect(caminho) as conexao:
        depois = {linha[1] for linha in conexao.execute("PRAGMA table_info(cliente)")}
        registro = conexao.execute(
            "SELECT email, cpf FROM cliente WHERE email = ?",
            ("legado@example.com",),
        ).fetchone()
        indices = {linha[1] for linha in conexao.execute("PRAGMA index_list(cliente)")}

    assert "cpf" in depois
    assert registro == ("legado@example.com", None)
    assert "uq_cliente_cpf_compat" in indices
