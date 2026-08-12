"""Testes da regra do cupom BEMVINDO."""

from decimal import Decimal

from aplicacao import banco
from aplicacao.modelos import Pedido, Produto


def test_bemvindo_e_registrado_no_primeiro_pedido(
    cliente_http, login, adicionar, aplicacao
):
    adicionar(1, 1)
    login()
    cliente_http.post(
        "/carrinho/cupom",
        data={"cupom": "BEMVINDO"},
        follow_redirects=True,
    )

    revisao = cliente_http.get("/pedidos/revisar")
    assert "Desconto · BEMVINDO" in revisao.text
    assert "R$ 9,00" in revisao.text

    resposta = cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "retirada", "forma_pagamento": "na_entrega"},
        follow_redirects=True,
    )
    assert "Pedido Recebido" in resposta.text
    assert "BEMVINDO" in resposta.text

    with aplicacao.app_context():
        pedido = banco.session.scalar(banco.select(Pedido))
        assert pedido.valor_total == Decimal("9.00")
        assert pedido.detalhes_checkout.cupom_codigo == "BEMVINDO"
        assert pedido.detalhes_checkout.valor_desconto == Decimal("1.00")
        assert banco.session.get(Produto, 1).estoque == 9

    with cliente_http.session_transaction() as sessao:
        assert "cupom_aplicado" not in sessao
        assert "carrinho" not in sessao


def test_bemvindo_nao_pode_ser_reutilizado_pelo_mesmo_cpf(
    cliente_http, login, adicionar, aplicacao
):
    adicionar(1, 1)
    login()
    cliente_http.post("/carrinho/cupom", data={"cupom": "BEMVINDO"})
    cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "retirada", "forma_pagamento": "na_entrega"},
    )

    adicionar(1, 1)
    resposta = cliente_http.post(
        "/carrinho/cupom",
        data={"cupom": "BEMVINDO"},
        follow_redirects=True,
    )

    assert "válido somente na primeira compra deste CPF" in resposta.text
    assert "R$ 10,00" in resposta.text
    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(banco.func.count(Pedido.id))) == 1


def test_primeiro_pedido_sem_cupom_nao_deixa_bemvindo_disponivel_depois(
    cliente_http, login, adicionar, aplicacao
):
    adicionar(1, 1)
    login()
    cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "retirada", "forma_pagamento": "na_entrega"},
    )

    adicionar(1, 1)
    resposta = cliente_http.post(
        "/carrinho/cupom",
        data={"cupom": "BEMVINDO"},
        follow_redirects=True,
    )

    assert "válido somente na primeira compra deste CPF" in resposta.text
    with aplicacao.app_context():
        pedido = banco.session.scalar(banco.select(Pedido))
        assert pedido.valor_total == Decimal("10.00")
        assert pedido.detalhes_checkout.valor_desconto == Decimal("0.00")
