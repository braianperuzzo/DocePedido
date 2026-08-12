"""Testes de carrinho da aplicação."""

from decimal import Decimal

from aplicacao import banco, criar_aplicacao
from aplicacao.controladores.carrinho import itens_e_total
from aplicacao.modelos import Pedido


def test_adicionar_produto_e_visualizar(adicionar, cliente_http):
    resposta = adicionar(1, 2)
    assert "Chocolate foi Adicionado ao Carrinho." in resposta.text
    resposta = cliente_http.get("/carrinho")
    assert "Chocolate" in resposta.text
    assert "R$ 20,00" in resposta.text


def test_adicionar_produto_existente_soma_quantidade(adicionar, cliente_http):
    adicionar(1, 2)
    adicionar(1, 3)
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"]["1"] == 5


def test_adicao_nao_redireciona_para_referencia_externa(cliente_http):
    resposta = cliente_http.post(
        "/carrinho/adicionar/1",
        data={"quantidade": 1},
        headers={"Referer": "https://example.com/pagina"},
    )

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/produtos")
    assert "example.com" not in resposta.headers["Location"]


def test_carrinho_descarta_estado_malformado_e_produto_inexistente(cliente_http):
    with cliente_http.session_transaction() as sessao:
        sessao["carrinho"] = {
            "1": 2,
            "999": 1,
            "texto": "invalido",
            "2": -1,
        }

    resposta = cliente_http.get("/carrinho")
    assert resposta.status_code == 200
    assert "Chocolate" in resposta.text

    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}


def test_alterar_quantidade(adicionar, cliente_http):
    adicionar(1, 1)
    cliente_http.post("/carrinho/atualizar/1", data={"quantidade": 4})
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"]["1"] == 4


def test_atualizacao_ajax_retorna_valores_recalculados(adicionar, cliente_http):
    adicionar(1, 1)
    adicionar(2, 2)

    resposta = cliente_http.post(
        "/carrinho/atualizar/1",
        data={"quantidade": 3},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 200
    assert resposta.json == {
        "ok": True,
        "produto_id": 1,
        "quantidade": 3,
        "subtotal": "R$ 30,00",
        "subtotal_carrinho": "R$ 60,00",
        "desconto": "R$ 0,00",
        "total": "R$ 60,00",
        "cupom": False,
        "quantidade_carrinho": 5,
    }


def test_cupom_bemvindo_da_dez_por_cento_na_primeira_compra(
    adicionar, cliente_http, login
):
    adicionar(1, 2)
    login()

    resposta = cliente_http.post(
        "/carrinho/cupom",
        data={"cupom": "bemvindo"},
        follow_redirects=True,
    )

    assert "Cupom BEMVINDO aplicado" in resposta.text
    assert "10% de desconto" in resposta.text
    assert "R$ 18,00" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert sessao["cupom_aplicado"] == "BEMVINDO"


def test_cupom_bemvindo_e_recusado_quando_cpf_ja_tem_pedido(
    adicionar, cliente_http, login, aplicacao
):
    with aplicacao.app_context():
        banco.session.add(
            Pedido(cliente_id=1, status="Recebido", valor_total=Decimal("10.00"))
        )
        banco.session.commit()

    adicionar(1, 1)
    login()
    resposta = cliente_http.post(
        "/carrinho/cupom",
        data={"cupom": "BEMVINDO"},
        follow_redirects=True,
    )

    assert "válido somente na primeira compra deste CPF" in resposta.text
    assert "R$ 10,00" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert "cupom_aplicado" not in sessao


def test_cupom_invalido_nao_altera_total(adicionar, cliente_http, login):
    adicionar(1, 2)
    login()
    resposta = cliente_http.post(
        "/carrinho/cupom",
        data={"cupom": "OUTRO"},
        follow_redirects=True,
    )

    assert "Cupom não encontrado" in resposta.text
    assert "R$ 20,00" in resposta.text


def test_atualizacao_ajax_recalcula_total_com_cupom(adicionar, cliente_http, login):
    adicionar(1, 1)
    login()
    cliente_http.post("/carrinho/cupom", data={"cupom": "BEMVINDO"})

    resposta = cliente_http.post(
        "/carrinho/atualizar/1",
        data={"quantidade": 3},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 200
    assert resposta.json["subtotal_carrinho"] == "R$ 30,00"
    assert resposta.json["desconto"] == "R$ 3,00"
    assert resposta.json["total"] == "R$ 27,00"
    assert resposta.json["cupom"] is True


def test_atualizacao_ajax_respeita_limite_de_estoque(adicionar, cliente_http):
    adicionar(1, 1)

    resposta = cliente_http.post(
        "/carrinho/atualizar/1",
        data={"quantidade": 11},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 422
    assert resposta.json["ok"] is False
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"]["1"] == 1


def test_adicao_ajax_retorna_mensagem_e_total_sem_flash(cliente_http):
    resposta = cliente_http.post(
        "/carrinho/adicionar/1",
        data={"quantidade": 2},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 200
    assert resposta.json == {
        "ok": True,
        "mensagem": "Chocolate foi Adicionado ao Carrinho.",
        "quantidade_carrinho": 2,
    }
    with cliente_http.session_transaction() as sessao:
        assert "_flashes" not in sessao


def test_adicao_ajax_retorna_erro_sem_alterar_carrinho(cliente_http):
    resposta = cliente_http.post(
        "/carrinho/adicionar/1",
        data={"quantidade": 11},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 422
    assert resposta.json == {
        "ok": False,
        "mensagem": "A quantidade solicitada ultrapassa o estoque disponível.",
    }
    with cliente_http.session_transaction() as sessao:
        assert not sessao.get("carrinho")
        assert "_flashes" not in sessao


def test_remover_produto(adicionar, cliente_http):
    adicionar(1)
    cliente_http.post("/carrinho/remover/1")
    with cliente_http.session_transaction() as sessao:
        assert "1" not in sessao.get("carrinho", {})


def test_esvaziar_carrinho_remove_cupom(adicionar, cliente_http, login):
    adicionar(1)
    adicionar(2)
    login()
    cliente_http.post("/carrinho/cupom", data={"cupom": "BEMVINDO"})
    cliente_http.post("/carrinho/esvaziar")
    with cliente_http.session_transaction() as sessao:
        assert "carrinho" not in sessao
        assert "cupom_aplicado" not in sessao


def test_quantidades_invalidas_sao_recusadas(adicionar, cliente_http):
    for quantidade in (0, -1, "texto"):
        resposta = adicionar(1, quantidade)
        assert "quantidade inteira maior que zero" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert not sessao.get("carrinho")


def test_quantidade_acima_do_estoque_e_recusada(adicionar, cliente_http):
    resposta = adicionar(1, 11)
    assert "ultrapassa o estoque" in resposta.text
    with cliente_http.session_transaction() as sessao:
        assert not sessao.get("carrinho")


def test_produto_inexistente_e_inativo_sao_recusados(adicionar, cliente_http):
    assert "Produto não encontrado" in adicionar(999, 1).text
    assert "não está disponível" in adicionar(3, 1).text
    with cliente_http.session_transaction() as sessao:
        assert not sessao.get("carrinho")


def test_subtotais_e_total_usam_decimal(adicionar, aplicacao):
    adicionar(1, 2)
    adicionar(2, 1)
    cliente = aplicacao.test_client()
    with cliente.session_transaction() as destino:
        destino["carrinho"] = {"1": 2, "2": 1}
    with cliente:
        cliente.get("/carrinho")
        itens, total = itens_e_total()
        assert itens[0]["subtotal"] == Decimal("20.00")
        assert itens[1]["subtotal"] == Decimal("15.00")
        assert total == Decimal("35.00")


def test_carrinho_exibe_links_controles_e_cupom(adicionar, cliente_http, login):
    adicionar(1)
    login()

    resposta = cliente_http.get("/carrinho")
    html = resposta.text

    assert html.count('href="/produtos/1"') == 2
    assert ">Atualizar<" not in html
    assert "Tradicionais" not in html
    assert 'data-cart-item' in html
    assert 'data-cart-subtotal' in html
    assert 'data-cart-total' in html
    assert 'id="cupom"' in html
    assert 'placeholder="Digite seu Cupom"' in html
    assert 'class="coupon-section coupon-section-summary"' in html
    assert html.index('id="cupom"') < html.index("Revisar o Pedido")
    assert 'action="/carrinho/cupom"' in html
    assert 'action="/carrinho/remover/1"' in html
    assert "Remover Chocolate do carrinho" in html


def test_atualizacao_ajax_continua_exigindo_csrf(tmp_path):
    aplicacao = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-csrf",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'csrf.db'}",
            "INICIALIZAR_DADOS": False,
            "WTF_CSRF_ENABLED": True,
        }
    )
    cliente = aplicacao.test_client()
    with cliente.session_transaction() as sessao:
        sessao["carrinho"] = {"1": 1}

    resposta = cliente.post(
        "/carrinho/atualizar/1",
        data={"quantidade": 2},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert resposta.status_code == 400
