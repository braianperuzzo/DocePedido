"""Testes de dados pessoais e segurança da área Minha Conta."""

import importlib
import re
from datetime import datetime, timedelta, timezone

from aplicacao import banco
from aplicacao.modelos import (
    AlteracaoConta,
    Cliente,
    DispositivoConfiavel,
    SegurancaConta,
)

modulo_conta = importlib.import_module("aplicacao.controladores.conta")


def capturar_email(monkeypatch):
    """Intercepta o e-mail transacional e devolve o último conteúdo enviado."""
    capturado = {}

    def falso_envio(**mensagem):
        capturado.update(mensagem)

    monkeypatch.setattr(modulo_conta, "enviar_email", falso_envio)
    return capturado


def extrair_caminho_confirmacao(texto):
    """Extrai do e-mail o caminho do token sem depender do host de testes."""
    encontrado = re.search(r"https?://[^/]+(/minha-conta/confirmar/[A-Za-z0-9_-]+)", texto)
    assert encontrado is not None
    return encontrado.group(1)


def test_minha_conta_exige_login_e_exibe_acoes(cliente_http, login):
    resposta = cliente_http.get("/minha-conta")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]

    login()
    resposta = cliente_http.get("/minha-conta")
    assert resposta.status_code == 200
    assert "Meus Dados" in resposta.text
    assert "Editar Dados" in resposta.text
    assert "Alterar Senha" in resposta.text
    assert "Excluir Conta" in resposta.text
    assert "modal-excluir-conta" in resposta.text
    assert "Endereços" in resposta.text
    assert "Cupcakes Favoritos" in resposta.text
    assert "Meus Pedidos" in resposta.text
    assert 'id="perfil-cpf"' in resposta.text
    assert 'name="cpf"' not in resposta.text
    assert resposta.headers["Cache-Control"] == "no-store, private"


def test_edicao_de_dados_so_aplica_depois_do_email(
    cliente_http, login, aplicacao, monkeypatch
):
    login()
    email = capturar_email(monkeypatch)

    resposta = cliente_http.post(
        "/minha-conta/dados",
        data={
            "nome": "Ana Silva",
            "email": "ana.silva@example.com",
            "cpf": "529.982.247-25",
            "telefone": "(54) 99999-0000",
            "senha_atual": "segredo12",
        },
        follow_redirects=True,
    )
    assert "só serão alterados depois da confirmação" in resposta.text
    assert "CPF" not in email["texto"]

    with aplicacao.app_context():
        cliente = banco.session.get(Cliente, 1)
        assert cliente.nome == "Ana"
        assert cliente.email == "ana@example.com"
        assert cliente.cpf == "11144477735"
        assert banco.session.scalar(banco.select(AlteracaoConta)) is not None

    caminho = extrair_caminho_confirmacao(email["texto"])
    resposta = cliente_http.get(caminho, follow_redirects=True)
    assert "Dados atualizados e confirmados com sucesso" in resposta.text

    with aplicacao.app_context():
        cliente = banco.session.get(Cliente, 1)
        assert cliente.nome == "Ana Silva"
        assert cliente.email == "ana.silva@example.com"
        assert cliente.cpf == "11144477735"
        assert cliente.telefone == "54999990000"

    pagina = cliente_http.get("/minha-conta")
    assert pagina.status_code == 200
    assert "111.444.777-35" in pagina.text
    assert "(54) 99999.0000" in pagina.text


def test_conta_aceita_somente_numero_celular(
    cliente_http, login, aplicacao, monkeypatch
):
    login()
    email = capturar_email(monkeypatch)

    resposta = cliente_http.post(
        "/minha-conta/dados",
        data={
            "nome": "Ana",
            "email": "ana@example.com",
            "telefone": "(54) 3333-4444",
            "senha_atual": "segredo12",
        },
        follow_redirects=True,
    )

    assert "Informe um celular com DDD" in resposta.text
    assert email == {}
    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(AlteracaoConta)) is None


def test_troca_de_senha_confirma_por_email_e_mantem_sessao(
    cliente_http, login, aplicacao, monkeypatch
):
    login()
    email = capturar_email(monkeypatch)

    resposta = cliente_http.post(
        "/minha-conta/senha",
        data={
            "senha_atual": "segredo12",
            "nova_senha": "Nova@1234",
            "confirmacao_nova_senha": "Nova@1234",
        },
        follow_redirects=True,
    )
    assert "A Senha Atual continua válida até você confirmar" in resposta.text

    with aplicacao.app_context():
        cliente = banco.session.get(Cliente, 1)
        assert cliente.verificar_senha("segredo12")
        assert not cliente.verificar_senha("Nova@1234")

    caminho = extrair_caminho_confirmacao(email["texto"])
    resposta = cliente_http.get(caminho, follow_redirects=True)
    assert "Senha Atualizada e confirmada com sucesso" in resposta.text
    assert resposta.request.path == "/minha-conta"

    with aplicacao.app_context():
        cliente = banco.session.get(Cliente, 1)
        assert cliente.verificar_senha("Nova@1234")
        assert not cliente.verificar_senha("segredo12")

    assert cliente_http.get("/minha-conta").status_code == 200


def test_senha_atual_incorreta_nao_cria_solicitacao(
    cliente_http, login, aplicacao, monkeypatch
):
    login()
    email = capturar_email(monkeypatch)

    resposta = cliente_http.post(
        "/minha-conta/senha",
        data={
            "senha_atual": "incorreta",
            "nova_senha": "Nova@1234",
            "confirmacao_nova_senha": "Nova@1234",
        },
        follow_redirects=True,
    )
    assert "Senha Atual incorreta" in resposta.text
    assert email == {}

    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(AlteracaoConta)) is None


def test_exclusao_da_conta_so_ocorre_depois_da_confirmacao_por_email(
    cliente_http, login, aplicacao, monkeypatch
):
    login()
    email = capturar_email(monkeypatch)

    with aplicacao.app_context():
        banco.session.add(SegurancaConta(cliente_id=1))
        banco.session.add(
            DispositivoConfiavel(
                cliente_id=1,
                token_hash="a" * 64,
                expira_em=datetime.now(timezone.utc) + timedelta(days=1),
            )
        )
        banco.session.commit()

    resposta = cliente_http.post("/minha-conta/excluir", follow_redirects=True)

    assert "Sua conta continua ativa até você confirmar" in resposta.text
    assert email["destinatario"] == "ana@example.com"
    assert "Confirme a exclusão da sua conta" in email["assunto"]

    with aplicacao.app_context():
        assert banco.session.get(Cliente, 1) is not None
        alteracao = banco.session.scalar(
            banco.select(AlteracaoConta).where(AlteracaoConta.tipo == "exclusao")
        )
        assert alteracao is not None

    caminho = extrair_caminho_confirmacao(email["texto"])
    resposta = cliente_http.get(caminho, follow_redirects=True)

    assert "Sua conta foi excluída com sucesso" in resposta.text
    with aplicacao.app_context():
        assert banco.session.get(Cliente, 1) is None
        assert banco.session.scalar(banco.select(AlteracaoConta)) is None
        assert banco.session.get(SegurancaConta, 1) is None
        assert (
            banco.session.scalar(
                banco.select(DispositivoConfiavel).where(
                    DispositivoConfiavel.cliente_id == 1
                )
            )
            is None
        )

    resposta_conta = cliente_http.get("/minha-conta")
    assert resposta_conta.status_code == 302
    assert "/login" in resposta_conta.headers["Location"]
