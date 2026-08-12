"""Testes de seo da aplicação."""

import json
from xml.etree import ElementTree

from aplicacao import banco
from aplicacao.modelos import Produto


def test_robots_referencia_sitemap_e_bloqueia_areas_privadas(aplicacao):
    aplicacao.config["SITE_URL"] = "https://loja.exemplo"
    resposta = aplicacao.test_client().get("/robots.txt")

    assert resposta.status_code == 200
    assert resposta.mimetype == "text/plain"
    assert "Disallow: /carrinho" in resposta.text
    assert "Disallow: /pedidos" in resposta.text
    assert "Sitemap: https://loja.exemplo/sitemap.xml" in resposta.text


def test_sitemap_lista_publicas_e_exclui_produto_inativo(aplicacao):
    aplicacao.config["SITE_URL"] = "https://loja.exemplo"
    with aplicacao.app_context():
        banco.session.get(Produto, 2).ativo = False
        banco.session.commit()

    resposta = aplicacao.test_client().get("/sitemap.xml")
    raiz = ElementTree.fromstring(resposta.data)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [elemento.text for elemento in raiz.findall("s:url/s:loc", namespace)]

    assert resposta.status_code == 200
    assert resposta.mimetype == "application/xml"
    assert "https://loja.exemplo/" in urls
    assert "https://loja.exemplo/produtos" in urls
    assert "https://loja.exemplo/cookies" in urls
    for caminho in ("sobre", "faq", "entrega", "trocas-e-cancelamentos"):
        assert f"https://loja.exemplo/{caminho}" in urls
    assert "https://loja.exemplo/produtos/1" in urls
    assert "https://loja.exemplo/produtos/2" not in urls
    assert all(
        all(
            privada not in url
            for privada in (
                "/login",
                "/cadastro",
                "/carrinho",
                "/pedidos",
                "/buscar",
                "/offline",
            )
        )
        for url in urls
    )


def test_paginas_institucionais_publicas(cliente_http):
    for caminho in ("/sobre", "/faq", "/entrega", "/trocas-e-cancelamentos"):
        resposta = cliente_http.get(caminho)
        assert resposta.status_code == 200
        assert '<meta name="robots" content="index, follow">' in resposta.text
        assert (
            f'<link rel="canonical" href="http://localhost{caminho}">' in resposta.text
        )


def test_metadados_publicos_privados_e_json_ld(cliente_http, aplicacao):
    aplicacao.config["SITE_URL"] = "https://loja.exemplo"

    produto = cliente_http.get("/produtos/1")
    assert '<meta name="robots" content="index, follow">' in produto.text
    assert (
        '<link rel="canonical" href="https://loja.exemplo/produtos/1">' in produto.text
    )
    assert (
        '<meta property="og:title" content="Chocolate | Doce Pedido">' in produto.text
    )
    assert '<meta name="twitter:card" content="summary_large_image">' in produto.text

    inicio = cliente_http.get("/")
    assert '<meta name="description"' in inicio.text
    assert '"@type": "Organization"' in inicio.text
    assert '"@type": "WebSite"' in inicio.text

    carrinho = cliente_http.get("/carrinho")
    assert '<meta name="robots" content="noindex, nofollow">' in carrinho.text
    assert 'rel="canonical"' not in carrinho.text


def test_dados_comerciais_sao_opcionais_no_rodape_e_json_ld(aplicacao):
    """Garante que contato e endereço só sejam publicados quando configurados."""
    cliente = aplicacao.test_client()
    pagina_sem_contato = cliente.get("/").text

    assert '"email"' not in pagina_sem_contato
    assert '"telephone"' not in pagina_sem_contato
    assert '"address"' not in pagina_sem_contato
    assert 'href="mailto:' not in pagina_sem_contato
    assert 'href="tel:' not in pagina_sem_contato
    assert "Siga a Doce Pedido" not in pagina_sem_contato

    aplicacao.config.update(
        SITE_EMAIL="responsavel@example.org",
        SITE_TELEPHONE="+551100000000",
        SITE_TELEPHONE_DISPLAY="+55 11 0000-0000",
        SITE_ADDRESS_STREET="Avenida Exemplo, 1",
        SITE_ADDRESS_LOCALITY="Cidade Exemplo",
        SITE_ADDRESS_REGION="EX",
        SITE_ADDRESS_COUNTRY="BR",
        SITE_INSTAGRAM_URL="https://example.org/rede",
    )
    pagina_configurada = cliente.get("/").text

    assert '"email": "responsavel@example.org"' in pagina_configurada
    assert '"telephone": "+551100000000"' in pagina_configurada
    assert '"address": {' in pagina_configurada
    assert 'href="mailto:responsavel@example.org"' in pagina_configurada
    assert 'href="tel:+551100000000"' in pagina_configurada
    assert "Siga a Doce Pedido" in pagina_configurada


def test_manifesto_e_verificacoes_opcionais(aplicacao):
    cliente = aplicacao.test_client()
    manifesto = cliente.get("/site.webmanifest")

    assert manifesto.status_code == 200
    assert manifesto.mimetype == "application/manifest+json"
    assert json.loads(manifesto.data)["name"] == "Doce Pedido"
    assert "google-site-verification" not in cliente.get("/").text

    aplicacao.config["GOOGLE_SITE_VERIFICATION"] = "codigo-google"
    aplicacao.config["BING_SITE_VERIFICATION"] = "codigo-bing"
    pagina = cliente.get("/").text
    assert 'name="google-site-verification" content="codigo-google"' in pagina
    assert 'name="msvalidate.01" content="codigo-bing"' in pagina
