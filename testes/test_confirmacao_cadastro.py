"""Testes do fluxo de confirmação de cadastro por e-mail."""

from importlib import import_module

from aplicacao import banco
from aplicacao.modelos import Cliente
from aplicacao.servicos.email import ErroEnvioEmail
from aplicacao.servicos.tokens import (
    gerar_token_confirmacao_email,
    gerar_token_redefinicao,
)

modulo_autenticacao = import_module("aplicacao.controladores.autenticacao")

DADOS_CADASTRO = {
    "nome": "Carlos",
    "cpf": "529.982.247-25",
    "email": "carlos@example.com",
    "senha": "Doce@123",
    "confirmacao_senha": "Doce@123",
}


def test_cadastro_cria_conta_pendente_e_envia_confirmacao(
    cliente_http, aplicacao, monkeypatch
):
    enviados = []
    monkeypatch.setattr(
        modulo_autenticacao,
        "enviar_email",
        lambda **dados: enviados.append(dados),
    )

    resposta = cliente_http.post(
        "/cadastro", data=DADOS_CADASTRO, follow_redirects=True
    )

    assert "Cadastro Realizado com Sucesso. Confira seu E-mail para Confirmar sua Conta." in resposta.text
    assert len(enviados) == 1
    assert enviados[0]["destinatario"] == "carlos@example.com"
    assert enviados[0]["assunto"] == "Confirme seu Cadastro na Doce Pedido"
    assert "Confirmar Minha Conta" in enviados[0]["html"]
    assert "/confirmar-email/" in enviados[0]["html"]
    assert "/confirmar-email/" in enviados[0]["texto"]
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "carlos@example.com")
        )
        assert cliente is not None
        assert cliente.ativo is False
        assert cliente.cpf == "52998224725"
        assert cliente.verificar_senha("Doce@123")


def test_conta_pendente_nao_faz_login(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = Cliente(
            nome="Carlos",
            cpf="52998224725",
            email="carlos@example.com",
            ativo=False,
        )
        cliente.definir_senha("Doce@123")
        banco.session.add(cliente)
        banco.session.commit()

    resposta = cliente_http.post(
        "/login",
        data={"email": "carlos@example.com", "senha": "Doce@123"},
        follow_redirects=True,
    )

    assert "Confirme seu e-mail antes de acessar sua conta" in resposta.text
    assert "Meus Pedidos" not in resposta.text


def test_confirmacao_ativa_autentica_e_preserva_carrinho(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = Cliente(
            nome="Carlos",
            cpf="52998224725",
            email="carlos@example.com",
            ativo=False,
        )
        cliente.definir_senha("Doce@123")
        banco.session.add(cliente)
        banco.session.commit()
        token = gerar_token_confirmacao_email(cliente)
    with cliente_http.session_transaction() as sessao:
        sessao["carrinho"] = {"1": 2}

    resposta = cliente_http.get(
        f"/confirmar-email/{token}", follow_redirects=True
    )

    assert "Meus Pedidos" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "carlos@example.com")
        )
        assert cliente.ativo is True


def test_confirmacao_repetida_e_idempotente(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = Cliente(
            nome="Carlos",
            cpf="52998224725",
            email="carlos@example.com",
            ativo=False,
        )
        cliente.definir_senha("Doce@123")
        banco.session.add(cliente)
        banco.session.commit()
        token = gerar_token_confirmacao_email(cliente)

    primeira = cliente_http.get(f"/confirmar-email/{token}")
    segunda = cliente_http.get(f"/confirmar-email/{token}", follow_redirects=True)

    assert primeira.status_code == 302
    assert segunda.status_code == 200


def test_token_de_redefinicao_nao_confirma_cadastro(cliente_http, aplicacao):
    with aplicacao.app_context():
        cliente = Cliente(
            nome="Carlos",
            cpf="52998224725",
            email="carlos@example.com",
            ativo=False,
        )
        cliente.definir_senha("Doce@123")
        banco.session.add(cliente)
        banco.session.commit()
        token = gerar_token_redefinicao(cliente)

    resposta = cliente_http.get(f"/confirmar-email/{token}", follow_redirects=True)

    assert "link de confirmação não é válido" in resposta.text
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "carlos@example.com")
        )
        assert cliente.ativo is False


def test_reenvio_de_pendente_nao_duplica_conta(cliente_http, aplicacao, monkeypatch):
    enviados = []
    monkeypatch.setattr(
        modulo_autenticacao,
        "enviar_email",
        lambda **dados: enviados.append(dados),
    )
    cliente_http.post("/cadastro", data=DADOS_CADASTRO)
    resposta = cliente_http.post(
        "/cadastro", data=DADOS_CADASTRO, follow_redirects=True
    )

    assert "aguardando confirmação" in resposta.text
    assert len(enviados) == 2
    with aplicacao.app_context():
        clientes = banco.session.scalars(
            banco.select(Cliente).where(Cliente.email == "carlos@example.com")
        ).all()
        assert len(clientes) == 1


def test_falha_no_email_nao_deixa_cadastro_inconsistente(
    cliente_http, aplicacao, monkeypatch
):
    def falhar(**_dados):
        raise ErroEnvioEmail("falha simulada")

    monkeypatch.setattr(modulo_autenticacao, "enviar_email", falhar)

    resposta = cliente_http.post("/cadastro", data=DADOS_CADASTRO)

    assert "Não foi Possível enviar a confirmação" in resposta.text
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "carlos@example.com")
        )
        assert cliente is None
