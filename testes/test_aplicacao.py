"""Testes de criação e conteúdo básico da aplicação."""

from html.parser import HTMLParser

from flask import url_for

from aplicacao import banco
from aplicacao.dados_iniciais import criar_dados_iniciais
from aplicacao.modelos import Categoria, Produto
from testes.conftest import normalizar_html


def test_criacao_da_aplicacao(aplicacao):
    assert aplicacao.config["TESTING"] is True
    with aplicacao.app_context():
        assert set(banco.metadata.tables) == {
            "alteracao_conta",
            "categoria",
            "cliente",
            "detalhe_pedido",
            "dispositivo_confiavel",
            "endereco",
            "favorito",
            "item_pedido",
            "pedido",
            "produto",
            "seguranca_conta",
        }


def test_dados_iniciais_completam_base_parcial_sem_duplicar(aplicacao):
    """Garante que um banco parcialmente preenchido também receba o catálogo padrão."""
    with aplicacao.app_context():
        criar_dados_iniciais()
        criar_dados_iniciais()

        categorias = set(
            banco.session.scalars(banco.select(Categoria.nome)).all()
        )
        produtos = banco.session.scalars(banco.select(Produto)).all()
        nomes_produtos = [produto.nome for produto in produtos]

        assert {"Tradicionais", "Especiais", "Kits"}.issubset(categorias)
        for nome in (
            "Cupcake de Chocolate",
            "Cupcake de Baunilha",
            "Cupcake Red Velvet",
            "Cupcake de Morango",
            "Kit com 6 Cupcakes",
        ):
            assert nomes_produtos.count(nome) == 1


def test_pagina_inicial_exibe_destaques(cliente_http):
    resposta = cliente_http.get("/")
    assert resposta.status_code == 200
    assert "Chocolate" in resposta.text
    assert "Inativo" not in resposta.text


def test_pagina_inicial_mantem_conteudo_essencial_sem_javascript(cliente_http):
    pagina = normalizar_html(cliente_http.get("/").text)

    assert "data-reveal" not in pagina
    assert ">Ver Produto</span>" in pagina
    assert ">Adicionar</span>" in pagina
    assert 'class="col-lg-6 hero-media"' in pagina
    assert "data-product-carousel" in pagina


class _LinksDeProdutoDaHome(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        classes = set(atributos.get("class", "").split())
        if tag == "a" and (
            {"product-image-link", "product-title-link", "icon-action"} & classes
        ):
            self.links.append(atributos.get("href"))


def test_links_dos_produtos_da_home_usam_rota_canonica(cliente_http, aplicacao):
    resposta = cliente_http.get("/")
    parser = _LinksDeProdutoDaHome()
    parser.feed(resposta.text)

    with aplicacao.test_request_context():
        produtos = banco.session.scalars(
            banco.select(Produto)
            .where(Produto.ativo.is_(True))
            .order_by(Produto.id.asc())
            .limit(8)
        ).all()
        rotas_canonicas = {
            url_for("produtos.detalhes", produto_id=produto.id) for produto in produtos
        }

    assert parser.links
    assert set(parser.links) == rotas_canonicas
    assert all(parser.links.count(rota) == 3 for rota in rotas_canonicas)
    assert all(cliente_http.get(link).status_code == 200 for link in set(parser.links))


def test_pagina_inicial_usa_textos_revisados(cliente_http):
    """Protege os principais textos estáveis da apresentação da Home."""
    pagina = cliente_http.get("/").text

    textos_esperados = (
        "Cupcakes para Diferentes Momentos",
        "Conhecer os Sabores",
        "Favoritos da Doce Pedido",
        "Ver Todos os Produtos",
        "Cuidado em Cada Detalhe",
        "Conhecer a Doce Pedido",
    )

    textos_ausentes = [texto for texto in textos_esperados if texto not in pagina]

    assert not textos_ausentes, (
        "A Home não contém os seguintes textos principais: "
        + ", ".join(textos_ausentes)
    )


def test_faq_usa_titulos_padronizados(cliente_http):
    pagina = cliente_http.get("/faq").text

    for titulo in (
        "Como Faço um Pedido?",
        "Preciso Criar uma Conta?",
        "Como Funciona o Cupom BEMVINDO?",
        "Quais Formas de Pagamento Estão Disponíveis?",
        "Como Funcionam Privacidade e Cookies?",
    ):
        assert titulo in pagina
