"""Testes de pedidos da aplicação."""

import importlib
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from aplicacao import banco
from aplicacao.modelos import DetalhePedido, Endereco, ItemPedido, Pedido, Produto
from testes.conftest import normalizar_html

modulo_pedidos = importlib.import_module("aplicacao.controladores.pedidos")


def criar_endereco(
    aplicacao,
    cliente_id=1,
    nome="Casa",
    principal=True,
    logradouro="Rua das Flores",
    numero="123",
):
    """Cria um endereço previsível para cenários de checkout."""
    with aplicacao.app_context():
        endereco = Endereco(
            cliente_id=cliente_id,
            nome=nome,
            cep="95000000",
            logradouro=logradouro,
            numero=numero,
            complemento="Apto 4",
            bairro="Centro",
            cidade="Caxias do Sul",
            uf="RS",
            referencia="Próximo à praça",
            principal=principal,
        )
        banco.session.add(endereco)
        banco.session.commit()
        return endereco.id


def test_exige_login_para_revisar_e_preserva_carrinho(adicionar, cliente_http):
    adicionar(1, 2)
    resposta = cliente_http.get("/pedidos/revisar", follow_redirects=True)
    assert "finalizar seu pedido" in resposta.text
    assert "carrinho foi preservado" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}


def test_nao_permite_finalizar_carrinho_vazio(cliente_http, login):
    login()
    resposta = cliente_http.get("/pedidos/revisar", follow_redirects=True)
    assert "carrinho está vazio" in resposta.text


def test_revisao_exibe_checkout_com_endereco_frete_e_pagamento(
    adicionar, cliente_http, login, aplicacao
):
    criar_endereco(aplicacao)
    adicionar(1, 2)
    adicionar(2, 1)
    login()

    resposta = cliente_http.get("/pedidos/revisar")
    html = normalizar_html(resposta.text)

    assert "Revisar Pedido" in html
    assert "Rua das Flores, 123 - Apto 4" in html
    assert "Frete grátis" in html
    assert "Pagamento Presencial" in html
    assert "Pix Online" in html
    assert "Cartão de Crédito Online" in html
    assert "Retirar na Loja" in html
    assert "R$ 35,00" in html
    assert 'value="pix" disabled' in html
    assert 'value="cartao" disabled' in html
    assert 'name="endereco_id"' in html
    assert "A confirmação será enviada para ana@example.com" in html
    assert 'class="checkout-summary-product" href="/produtos/1"' in html
    assert 'class="checkout-summary-product" href="/produtos/2"' in html
    assert "checkout-summary-thumb" in html


def test_checkout_permite_escolher_outro_endereco_salvo(
    adicionar, cliente_http, login, aplicacao
):
    criar_endereco(aplicacao)
    trabalho_id = criar_endereco(
        aplicacao,
        nome="Trabalho",
        principal=False,
        logradouro="Rua do Trabalho",
        numero="500",
    )
    adicionar(1, 1)
    login()

    revisao = cliente_http.get("/pedidos/revisar")
    assert "Casa · Principal" in revisao.text
    assert "Trabalho" in revisao.text

    resposta = cliente_http.post(
        "/pedidos/confirmar",
        data={
            "tipo_entrega": "entrega",
            "forma_pagamento": "na_entrega",
            "endereco_id": str(trabalho_id),
        },
        follow_redirects=True,
    )
    assert "Pedido Recebido" in resposta.text

    with aplicacao.app_context():
        detalhe = banco.session.scalar(banco.select(DetalhePedido))
        assert "Rua do Trabalho, 500 - Apto 4" in detalhe.endereco_entrega


def test_sem_endereco_prioriza_retirada_na_loja(adicionar, cliente_http, login):
    adicionar(1, 1)
    login()

    resposta = cliente_http.get("/pedidos/revisar")
    html = normalizar_html(resposta.text)

    assert 'value="entrega" data-receipt-option disabled' in html
    assert 'value="retirada" data-receipt-option checked' in html
    assert "Cadastrar endereço" in html


def test_confirmacao_cria_pedido_checkout_reduz_estoque_e_limpa_carrinho(
    adicionar, cliente_http, login, aplicacao
):
    criar_endereco(aplicacao)
    adicionar(1, 2)
    adicionar(2, 1)
    login()

    resposta = cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "entrega", "forma_pagamento": "na_entrega"},
        follow_redirects=True,
    )
    assert "Pedido Recebido" in resposta.text

    with aplicacao.app_context():
        pedido = banco.session.scalar(banco.select(Pedido))
        assert pedido.status == "Recebido"
        assert pedido.valor_total == Decimal("35.00")
        assert len(pedido.itens) == 2
        assert pedido.itens[0].valor_unitario == Decimal("10.00")
        assert pedido.itens[0].subtotal == Decimal("20.00")
        assert pedido.detalhes_checkout.tipo_entrega == "Entrega"
        assert pedido.detalhes_checkout.forma_pagamento == "Presencial"
        assert pedido.detalhes_checkout.valor_frete == Decimal("0.00")
        assert (
            "Rua das Flores, 123 - Apto 4"
            in pedido.detalhes_checkout.endereco_entrega
        )
        assert banco.session.get(Produto, 1).estoque == 8
        assert banco.session.get(Produto, 2).estoque == 4

    with cliente_http.session_transaction() as sessao:
        assert "carrinho" not in sessao


def test_retirada_na_loja_nao_grava_endereco(adicionar, cliente_http, login, aplicacao):
    adicionar(1, 1)
    login()

    resposta = cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "retirada", "forma_pagamento": "na_entrega"},
        follow_redirects=True,
    )
    assert "Retirada na Loja" in resposta.text

    with aplicacao.app_context():
        detalhe = banco.session.scalar(banco.select(DetalhePedido))
        assert detalhe.tipo_entrega == "Retirada na Loja"
        assert detalhe.forma_pagamento == "Presencial"
        assert detalhe.endereco_entrega is None
        assert detalhe.valor_frete == Decimal("0.00")


def test_pagamento_online_adulterado_e_rejeitado(
    adicionar, cliente_http, login, aplicacao
):
    adicionar(1, 1)
    login()

    resposta = cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "retirada", "forma_pagamento": "pix"},
        follow_redirects=True,
    )

    assert "pagamento disponível é somente presencial na entrega ou retirada" in resposta.text
    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(Pedido)) is None
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 1}


def test_confirmacao_dispara_email_com_resumo(
    adicionar, cliente_http, login, aplicacao, monkeypatch
):
    criar_endereco(aplicacao)
    adicionar(1, 1)
    login()
    email = {}

    def falso_envio(**mensagem):
        email.update(mensagem)

    monkeypatch.setattr(modulo_pedidos, "enviar_email", falso_envio)

    resposta = cliente_http.post(
        "/pedidos/confirmar",
        data={"tipo_entrega": "entrega", "forma_pagamento": "na_entrega"},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert email["destinatario"] == "ana@example.com"
    assert "Pedido nº 1 confirmado" in email["assunto"]
    assert "Frete" in email["html"]
    assert "Grátis" in email["html"]
    assert "Rua das Flores, 123 - Apto 4" in email["html"]
    assert "Pagamento:</strong> Presencial" in email["html"]


def test_estoque_e_validado_novamente(adicionar, cliente_http, login, aplicacao):
    adicionar(1, 5)
    login()
    with aplicacao.app_context():
        banco.session.get(Produto, 1).estoque = 2
        banco.session.commit()
    resposta = cliente_http.post("/pedidos/confirmar", follow_redirects=True)
    assert "Estoque insuficiente" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 5}
    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(Pedido)) is None


def test_produto_removido_do_banco_impede_confirmacao(cliente_http, login, aplicacao):
    with cliente_http.session_transaction() as sessao:
        sessao["carrinho"] = {"999": 1}
    login()
    resposta = cliente_http.post("/pedidos/confirmar", follow_redirects=True)
    assert "produto do carrinho não foi encontrado" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert "carrinho" not in sessao


def test_falha_no_banco_faz_rollback_e_preserva_carrinho(
    adicionar, cliente_http, login, aplicacao, monkeypatch
):
    adicionar(1, 2)
    login()

    def falhar():
        raise SQLAlchemyError("falha simulada")

    monkeypatch.setattr(banco.session, "commit", falhar)
    resposta = cliente_http.post("/pedidos/confirmar", follow_redirects=True)
    assert "Não foi Possível registrar" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}
    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(Pedido)) is None
        assert banco.session.get(Produto, 1).estoque == 10


def criar_pedido(aplicacao, cliente_id=1):
    with aplicacao.app_context():
        produto = banco.session.get(Produto, 1)
        pedido = Pedido(
            cliente_id=cliente_id, status="Recebido", valor_total=Decimal("10.00")
        )
        pedido.itens.append(
            ItemPedido(
                produto=produto,
                quantidade=1,
                valor_unitario=Decimal("10.00"),
                subtotal=Decimal("10.00"),
            )
        )
        banco.session.add(pedido)
        banco.session.commit()
        return pedido.id


def test_lista_somente_pedidos_do_cliente(cliente_http, login, aplicacao):
    proprio = criar_pedido(aplicacao, 1)
    alheio = criar_pedido(aplicacao, 2)
    login()
    resposta = cliente_http.get("/pedidos")
    assert f"nº {proprio}" in resposta.text
    assert f"nº {alheio}" not in resposta.text
    assert "R$ 10,00" in resposta.text
    assert 'href="/produtos/1"' in resposta.text


def test_lista_exibe_dados_do_checkout(cliente_http, login, aplicacao):
    with aplicacao.app_context():
        produto = banco.session.get(Produto, 1)
        pedido = Pedido(
            cliente_id=1,
            status="Recebido",
            valor_total=Decimal("10.00"),
        )
        pedido.detalhes_checkout = DetalhePedido(
            tipo_entrega="Retirada na Loja",
            forma_pagamento="Presencial",
            valor_frete=Decimal("0.00"),
        )
        pedido.itens.append(
            ItemPedido(
                produto=produto,
                quantidade=1,
                valor_unitario=Decimal("10.00"),
                subtotal=Decimal("10.00"),
            )
        )
        banco.session.add(pedido)
        banco.session.commit()

    login()
    resposta = cliente_http.get("/pedidos")
    assert "Retirada na Loja · Presencial" in resposta.text
    assert "Frete grátis" in resposta.text


def test_detalhes_do_proprio_pedido(cliente_http, login, aplicacao):
    pedido_id = criar_pedido(aplicacao)
    login()
    resposta = cliente_http.get(f"/pedidos/{pedido_id}")
    assert resposta.status_code == 200
    assert "Chocolate" in resposta.text
    assert "Recebido" in resposta.text
    assert 'href="/produtos/1"' in resposta.text


def test_bloqueia_pedido_de_outro_cliente(cliente_http, login, aplicacao):
    pedido_id = criar_pedido(aplicacao, 2)
    login()
    resposta = cliente_http.get(f"/pedidos/{pedido_id}", follow_redirects=True)
    assert "Pedido não encontrado" in resposta.text
    assert "Chocolate" not in resposta.text


def test_pedido_inexistente(cliente_http, login):
    login()
    resposta = cliente_http.get("/pedidos/999", follow_redirects=True)
    assert "Pedido não encontrado" in resposta.text
