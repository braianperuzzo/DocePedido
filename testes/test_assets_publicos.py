"""Testes de assets publicos da aplicação."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image

from aplicacao import banco, criar_aplicacao
from aplicacao.modelos import Produto


class ColetorAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = set()

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        for nome in ("src", "href"):
            valor = atributos.get(nome, "")
            caminho = urlsplit(valor).path
            if caminho.startswith("/static/") or caminho.endswith(".webmanifest"):
                self.assets.add(caminho)


def test_paginas_publicas_referenciam_apenas_assets_existentes(tmp_path):
    app = criar_aplicacao(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'assets.db'}",
            "INICIALIZAR_DADOS": True,
        }
    )
    cliente = app.test_client()
    with app.app_context():
        ids = banco.session.scalars(banco.select(Produto.id)).all()

    paginas = [
        "/",
        "/produtos",
        "/buscar?q=cupcake",
        "/sobre",
        "/faq",
        "/entrega",
        "/trocas-e-cancelamentos",
        "/privacidade",
        "/cookies",
        "/termos",
        "/seguranca",
        "/offline",
        *[f"/produtos/{produto_id}" for produto_id in ids],
    ]
    assets = {"/manifest.webmanifest", "/service-worker.js"}
    for pagina in paginas:
        resposta = cliente.get(pagina)
        assert resposta.status_code == 200, pagina
        coletor = ColetorAssets()
        coletor.feed(resposta.get_data(as_text=True))
        assets.update(coletor.assets)

    manifesto = cliente.get("/manifest.webmanifest")
    assert manifesto.status_code == 200
    assets.update(icone["src"] for icone in manifesto.get_json()["icons"])
    for asset in assets:
        assert cliente.get(asset).status_code == 200, asset


def test_inicializacao_corrige_imagem_em_banco_existente(tmp_path):
    configuracao = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'existente.db'}",
        "INICIALIZAR_DADOS": True,
    }
    app = criar_aplicacao(configuracao)
    with app.app_context():
        chocolate = banco.session.scalar(
            banco.select(Produto).where(Produto.nome == "Cupcake de Chocolate")
        )
        chocolate.imagem = "imagens/cupcake_cholocate.png"
        banco.session.commit()

    app = criar_aplicacao(configuracao)
    with app.app_context():
        chocolate = banco.session.scalar(
            banco.select(Produto).where(Produto.nome == "Cupcake de Chocolate")
        )
        assert chocolate.imagem == "imagens/cupcake_chocolate.webp"


def test_imagem_inexistente_renderiza_placeholders_sem_requisitar_asset(
    cliente_http, aplicacao
):
    with aplicacao.app_context():
        produto = banco.session.get(Produto, 1)
        produto.nome = "Kit com 6 Cupcakes"
        produto.imagem = "imagens/nao-existe.png"
        banco.session.commit()

    paginas = {
        "/": ("image-placeholder hero-placeholder", 3),
        "/produtos": ("image-placeholder", 1),
        "/buscar?q=Kit": ("image-placeholder", 1),
        "/produtos/1": ("image-placeholder detail-placeholder", 1),
    }
    for pagina, (placeholder, quantidade_minima) in paginas.items():
        resposta = cliente_http.get(pagina)
        assert resposta.status_code == 200, pagina
        assert "nao-existe.png" not in resposta.text, pagina
        assert placeholder in resposta.text, pagina
        assert resposta.text.count("image-placeholder") >= quantidade_minima, pagina

        coletor = ColetorAssets()
        coletor.feed(resposta.text)
        assert "/static/imagens/nao-existe.png" not in coletor.assets, pagina


def test_imagens_de_produto_sao_webp_validos_leves_e_quadrados(tmp_path):
    raiz = Path(__file__).parents[1] / "aplicacao" / "static" / "imagens"
    produtos = sorted(raiz.glob("cupcake_*.webp"))

    app = criar_aplicacao(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'webp.db'}",
            "INICIALIZAR_DADOS": True,
        }
    )
    with app.app_context():
        imagens_referenciadas = banco.session.scalars(
            banco.select(Produto.imagem).where(Produto.imagem.is_not(None))
        ).all()

    assert len(produtos) == 5
    assert all(not imagem.lower().endswith(".png") for imagem in imagens_referenciadas)
    for caminho in produtos:
        assert caminho.stat().st_size < 200_000
        with Image.open(caminho) as imagem:
            assert imagem.format == "WEBP"
            imagem.verify()
        with Image.open(caminho) as imagem:
            assert imagem.width > 0
            assert imagem.height > 0
            assert imagem.width == imagem.height

    logo = raiz / "logo.png"
    assert logo.stat().st_size < 200_000
    with Image.open(logo) as imagem:
        assert imagem.size == (460, 215)
