"""Testes de produtos da aplicação."""

from decimal import Decimal

from aplicacao import banco
from aplicacao.modelos import Produto
from testes.conftest import normalizar_html


def test_catalogo_lista_apenas_produtos_ativos(cliente_http):
    resposta = cliente_http.get("/produtos")
    assert "Chocolate" in resposta.text
    assert "Morango" in resposta.text
    assert "Inativo" not in resposta.text


def test_catalogo_mantem_filtros_responsivos_e_combina_criterios(cliente_http):
    resposta = cliente_http.get(
        "/produtos?categoria=tradicionais&disponibilidade=disponivel"
        "&ordem=preco_asc&q=Chocolate"
    )

    assert resposta.status_code == 200
    assert 'id="catalog-filters" class="catalog-filters collapse"' in normalizar_html(
        resposta.text
    )
    assert 'aria-controls="catalog-filters"' in resposta.text
    assert "1 Produto Encontrado." in normalizar_html(resposta.text)
    assert "Chocolate" in resposta.text
    assert "Morango" not in resposta.text


def test_catalogo_e_busca_com_nome_de_produto_longo(cliente_http, aplicacao):
    nome = "Cupcake artesanal de chocolate com cobertura especial para celebrações"
    with aplicacao.app_context():
        referencia = banco.session.get(Produto, 1)
        banco.session.add(
            Produto(
                nome=nome,
                descricao="Descrição extensa para validar a estabilidade visual do card.",
                preco=Decimal("18.00"),
                estoque=4,
                ativo=True,
                categoria=referencia.categoria,
            )
        )
        banco.session.commit()

    assert nome in cliente_http.get("/produtos").text
    resposta_busca = cliente_http.get("/buscar?q=celebrações")
    assert resposta_busca.status_code == 200
    assert nome in resposta_busca.text
    assert "1 Produto Encontrado." in normalizar_html(resposta_busca.text)


def test_catalogo_exibe_contagem_com_frases_completas(cliente_http):
    assert "2 Produtos Encontrados." in normalizar_html(
        cliente_http.get("/produtos").text
    )
    assert "1 Produto Encontrado." in normalizar_html(
        cliente_http.get("/produtos?q=Chocolate").text
    )
    assert "Nenhum Produto Encontrado." in normalizar_html(
        cliente_http.get("/produtos?q=inexistente").text
    )


def test_detalhes_mostram_dados_do_produto(cliente_http):
    resposta = cliente_http.get("/produtos/1")
    assert resposta.status_code == 200
    conteudo = normalizar_html(resposta.text)
    assert "Chocolate" in conteudo
    assert "R$ 10,00" in conteudo
    assert "Disponível" in conteudo
    assert "Carrinho" in conteudo
    assert 'max="10"' in resposta.text
    assert 'aria-label="Diminuir quantidade"' in resposta.text
    assert 'aria-label="Aumentar quantidade"' in resposta.text


def test_detalhes_preservam_seo_e_breadcrumb_estruturado(cliente_http):
    resposta = cliente_http.get("/produtos/1")
    conteudo = resposta.text

    assert "application/ld+json" in conteudo
    assert "BreadcrumbList" in conteudo
    assert 'aria-label="Navegação estrutural"' in conteudo
    assert 'aria-current="page"' in conteudo


def test_produto_inexistente_retorna_404(cliente_http):
    assert cliente_http.get("/produtos/9999").status_code == 404


def test_produto_inativo_nao_e_exibido(cliente_http):
    resposta = cliente_http.get("/produtos/3")
    assert resposta.status_code == 404
    assert "não está disponível" in resposta.text
