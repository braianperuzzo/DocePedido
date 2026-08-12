"""Testes de busca da aplicação."""

from aplicacao import banco
from aplicacao.modelos import Produto
from testes.conftest import normalizar_html


def test_busca_por_nome_descricao_e_categoria(cliente_http):
    assert "Chocolate" in cliente_http.get("/buscar?q=Chocolate").text
    assert "Morango" in cliente_http.get("/buscar?q=Cupcake").text
    resposta_categoria = cliente_http.get("/buscar?q=Tradicionais")
    assert "Chocolate" in resposta_categoria.text
    assert "Morango" in resposta_categoria.text


def test_busca_e_case_insensitive_e_noindex(cliente_http):
    resposta = cliente_http.get("/buscar?q=chocolate")
    html = normalizar_html(resposta.text)
    assert resposta.status_code == 200
    assert "Chocolate" in html
    assert 'content="noindex, follow"' in html
    assert "1 Produto Encontrado." in html


def test_busca_vazia_redireciona_ao_catalogo(cliente_http):
    resposta = cliente_http.get("/buscar?q=   ")
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/produtos")


def test_busca_sem_resultados_e_produto_inativo(cliente_http, aplicacao):
    assert "Nenhum Produto Encontrado." in normalizar_html(
        cliente_http.get("/buscar?q=inexistente").text
    )
    with aplicacao.app_context():
        banco.session.get(Produto, 1).ativo = False
        banco.session.commit()
    resposta = normalizar_html(cliente_http.get("/buscar?q=Chocolate").text)
    assert 'href="/produtos/1"' not in resposta
    assert "Nenhum Produto Encontrado." in resposta


def test_busca_exibe_contagem_com_frases_completas(cliente_http):
    assert "2 Produtos Encontrados." in normalizar_html(
        cliente_http.get("/buscar?q=Tradicionais").text
    )
    assert "1 Produto Encontrado." in normalizar_html(
        cliente_http.get("/buscar?q=Chocolate").text
    )
    assert "Nenhum Produto Encontrado." in normalizar_html(
        cliente_http.get("/buscar?q=inexistente").text
    )
