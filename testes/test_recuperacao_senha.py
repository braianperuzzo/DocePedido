"""Testes do fluxo de recuperação de senha por e-mail."""

from importlib import import_module

from aplicacao import banco
from aplicacao.modelos import Cliente
from aplicacao.servicos.tokens import gerar_token_redefinicao

modulo_autenticacao = import_module("aplicacao.controladores.autenticacao")

NOVA_SENHA = "Nova@123"


def test_recuperacao_existente_envia_template_sem_expor_existencia(
    cliente_http, monkeypatch
):
    enviados = []
    monkeypatch.setattr(
        modulo_autenticacao,
        "enviar_email",
        lambda **dados: enviados.append(dados),
    )

    resposta = cliente_http.post(
        "/esqueci-senha",
        data={"email": "ana@example.com"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 200
    assert "Se houver uma conta cadastrada" in resposta.json["mensagem"]
    assert len(enviados) == 1
    assert enviados[0]["destinatario"] == "ana@example.com"
    assert enviados[0]["assunto"] == "Redefinição de Senha - Doce Pedido"
    assert "Redefinir Senha" in enviados[0]["html"]
    assert "/redefinir-senha/" in enviados[0]["html"]
    assert "/redefinir-senha/" in enviados[0]["texto"]


def test_recuperacao_inexistente_responde_igual_sem_enviar(cliente_http, monkeypatch):
    enviados = []
    monkeypatch.setattr(
        modulo_autenticacao,
        "enviar_email",
        lambda **dados: enviados.append(dados),
    )

    resposta = cliente_http.post(
        "/esqueci-senha", data={"email": "naoexiste@example.com"}
    )

    assert resposta.status_code == 200
    assert "Se houver uma conta cadastrada" in resposta.json["mensagem"]
    assert enviados == []


def test_recuperacao_recusa_email_malformado(cliente_http):
    resposta = cliente_http.post("/esqueci-senha", data={"email": "invalido"})

    assert resposta.status_code == 400
    assert resposta.json == {"ok": False, "mensagem": "Informe um e-mail válido."}


def test_redefinicao_altera_senha_invalida_token_e_autentica(
    cliente_http, aplicacao
):
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        token = gerar_token_redefinicao(cliente)
        hash_anterior = cliente.senha_hash

    resposta = cliente_http.post(
        f"/redefinir-senha/{token}",
        data={"senha": NOVA_SENHA, "confirmacao_senha": NOVA_SENHA},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Meus Pedidos" in resposta.text
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        assert cliente.senha_hash != hash_anterior
        assert cliente.verificar_senha(NOVA_SENHA)

    repeticao = cliente_http.get(f"/redefinir-senha/{token}")
    assert repeticao.status_code == 400
    assert "não é válido" in repeticao.text


def test_redefinicao_preserva_carrinho(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        token = gerar_token_redefinicao(cliente)
    with cliente_http.session_transaction() as sessao:
        sessao["carrinho"] = {"1": 2}

    cliente_http.post(
        f"/redefinir-senha/{token}",
        data={"senha": NOVA_SENHA, "confirmacao_senha": NOVA_SENHA},
    )

    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}


def test_redefinicao_recusa_senha_atual(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        token = gerar_token_redefinicao(cliente)

    resposta = cliente_http.post(
        f"/redefinir-senha/{token}",
        data={"senha": "segredo12", "confirmacao_senha": "segredo12"},
    )

    assert "uma letra maiúscula" in resposta.text
    assert "um caractere especial" in resposta.text


def test_pagina_redefinicao_tem_headers_privados(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        token = gerar_token_redefinicao(cliente)

    resposta = cliente_http.get(f"/redefinir-senha/{token}")

    assert resposta.status_code == 200
    assert resposta.headers["Cache-Control"] == "no-store, private"
    assert resposta.headers["X-Robots-Tag"] == "noindex, nofollow"
